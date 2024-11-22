from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Bet, BetParticipation
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Look up the user by email
        user = User.query.filter_by(email=email).first()

        if user:
            # Check password hash
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('Logged out successfully', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            # Create a new user and hash password
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Send reset email logic here
            send_reset_email(email)
            flash('An email has been sent with instructions to reset your password.', 'success')
        else:
            flash('Email not found.', 'error')
        return redirect(url_for('auth.forgot_password'))  # Redirect after POST
    return render_template('forgot_password.html')

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