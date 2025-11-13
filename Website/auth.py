from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Bet, BetParticipation
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask import session

auth = Blueprint('auth', __name__)

@auth.route('/choose-name', methods=['POST'])
def choose_name():
    username = request.form.get('username').strip()

    if len(username) < 2:
        flash('Username must be at least 2 characters.', category='error')
        return redirect(url_for('views.home'))

    user = User.query.filter_by(username=username).first()
    
    # This logic handles both new guests and existing guests
    if user:
        session['user_id'] = user.id
    else:
        # Create a new guest user with no password
        new_user = User(username=username, points=1000)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        
    flash(f'Welcome, {username}! You are playing as a guest.', category='success')
    return redirect(url_for('views.project_dashboard'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
            return render_template('login.html', user=current_user)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_registered:
            if password:
                if check_password_hash(user.password, password):
                    flash(f'Welcome back, {user.username}!', category='success')
                    login_user(user, remember=True)
                    # We should also handle the weekly points allowance here
                    return redirect(url_for('views.project_dashboard'))
                else:
                    flash('Incorrect password.', category='error')
                    # Render a page that asks for the password again
                    return render_template('password_prompt.html', username=username)
            else:
                # No password provided, so prompt for it
                return render_template('password_prompt.html', username=username)
        
        # Case 2: Username is NOT registered (or is a guest)
        else:
            session.clear() # Clear any previous session data
            session['guest_username'] = username
            flash(f'You are playing as a guest. Register to save your points!', category='info')
            return redirect(url_for('views.project_dashboard'))

    # If GET request, just redirect to home
    return redirect(url_for('views.home'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  
    flash('Logged out successfully', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['POST'])
def register():
    # User must be a guest to register
    if 'guest_username' not in session:
        flash('You must choose a guest name first.', category='error')
        return redirect(url_for('views.home'))

    username = session['guest_username']
    password = request.form.get('password')

    # Check if the name was taken while they were a guest
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('This username has just been registered. Please choose another.', category='error')
        session.pop('guest_username', None)
        return redirect(url_for('views.home'))

    # Validation
    if not password or len(password) < 7:
        flash('Password must be at least 7 characters.', category='error')
        return render_template('register_form.html', username=username)

    # Create the new user
    new_user = User(
        username=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        # You can set the initial points here if you want to reward registration
        points=session.get('guest_points', 1000) 
    )
    db.session.add(new_user)
    db.session.commit()

    # Log them in properly and clear the guest session
    session.pop('guest_username', None)
    login_user(new_user, remember=True)
    flash('Registration successful! Your account is now permanent.', category='success')
    
    return redirect(url_for('views.project_dashboard'))

@auth.route('/place-bet/<int:bet_id>', methods=['GET', 'POST'])
@login_required
def place_bet(bet_id):
    bet = Bet.query.get_or_404(bet_id)
    if request.method == 'POST':
        option = request.form.get('option')
        if option in bet.options:
            # Create a new BetParticipation entry
            new_participation = BetParticipation(user_id=current_user.id, bet_id=bet.id, option=option)
            db.session.add(new_participation)
            db.session.commit()
            flash('Bet placed successfully!', category='success')
            return redirect(url_for('views.view_bet', bet_id=bet.id))  # Redirect to the bet's details
        else:
            flash('Invalid betting option', category='error')

    return render_template('place_bet.html', bet=bet)


@auth.route('/bet-history')
@login_required
def bet_history():
    participations = BetParticipation.query.filter_by(user_id=current_user.id).all()
    return render_template('bet_history.html', participations=participations)