import os
from flask import Blueprint, g, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required  # Import login_required here
from .models import db, Bet, BetParticipation, BetResult, User

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/project-dashboard', methods=['GET', 'POST'])
def project_dashboard():
    # This block handles the form submission when a user places a bet.
    if request.method == 'POST':
        # Check if a user is logged in as a guest
        if not g.user:
            flash("You must choose a name first.", category="error")
            return redirect(url_for('views.home'))

        # Get data from the form
        event_id = request.form.get('event_id')
        bet_option = request.form.get('bet_option')
        wager_amount_str = request.form.get('wager_amount')

        # --- VALIDATION ---
        if not event_id or not bet_option or not wager_amount_str:
            flash("All fields are required!", category="error")
            return redirect(url_for('views.project_dashboard'))
        
        try:
            wager_amount = int(wager_amount_str)
            if wager_amount <= 0:
                flash("Wager must be a positive number.", category="error")
                return redirect(url_for('views.project_dashboard'))
        except ValueError:
            flash("Invalid wager amount.", category="error")
            return redirect(url_for('views.project_dashboard'))

        # Check if the user has enough points
        if g.user.points < wager_amount:
            flash("You do not have enough points to place that bet.", category="error")
            return redirect(url_for('views.project_dashboard'))
        
        try:
            g.user.points -= wager_amount
            new_participation = BetParticipation(
                user_id=g.user.id,
                bet_id=int(event_id),
                option=bet_option,
                wager_amount=wager_amount
            )
            db.session.add(new_participation)
            db.session.commit()
            flash(f"Bet placed successfully! Your new balance is {g.user.points} points.", category="success")
        
        except Exception as e:
            db.session.rollback() 
            flash("An error occurred while placing your bet.", category="error")
            app.logger.error(f"Error placing bet: {e}")

        return redirect(url_for('views.project_dashboard'))
    events = Bet.query.filter_by(is_active=True).all()
    return render_template('project_dashboard.html', events=events)


@views.route('/bet-history')
@login_required
def bet_history():
    bet_history = BetParticipation.query.filter_by(user_id=current_user.id).all()
    return render_template('bethistory.html', bet_history=bet_history)