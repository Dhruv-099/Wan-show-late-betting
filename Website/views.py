import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required  # Import login_required here
from .models import db, Bet, BetParticipation, BetResult, User

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/project-dashboard', methods=['GET', 'POST'])
def project_dashboard():
    if request.method == 'POST':
        event_id = request.form.get('event')
        bet_option = request.form.get('bet_option')
        username = current_user.name if current_user.is_authenticated else request.form.get('username')

        # Validation
        if not event_id or not bet_option or not username:
            flash("All fields are required!", category="error")
            return redirect(url_for('views.project_dashboard'))

        # Create and save the bet
        new_bet = Bet(event_id=event_id, user_name=username, bet_option=bet_option)
        try:
            db.session.add(new_bet)
            db.session.commit()
            flash("Bet placed successfully!", category="success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while placing your bet.", category="error")
            print(f"Error: {e}")

        return redirect(url_for('views.project_dashboard'))

    # Fetch events for dropdown
    events = Event.query.all()
    return render_template('project_dashboard.html', events=events)

@views.route('/bet-history')
@login_required
def bet_history():
    bet_history = BetParticipation.query.filter_by(user_id=current_user.id).all()
    return render_template('bethistory.html', bet_history=bet_history)