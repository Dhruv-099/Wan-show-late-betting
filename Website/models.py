from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

# Choices for weekdays
WEEKDAYS = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # Title of the event
    weekday = db.Column(db.Integer, nullable=False)  # Day of the week (0-6)
    options = db.Column(db.JSON, nullable=False)  # Betting options
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Bet creation time
    closing_time = db.Column(db.Time, nullable=False)  # Time on the day bets close
    is_active = db.Column(db.Boolean, default=True)  # Active status of the bet

    def __repr__(self):
        return f"<Bet {self.title} - {WEEKDAYS[self.weekday]}>"

    def get_next_occurrence(self):
        """Calculate the date of the next occurrence of the bet."""
        today = datetime.utcnow().date()
        today_weekday = today.weekday()
        days_until_next = (self.weekday - today_weekday + 7) % 7
        return today + timedelta(days=days_until_next)

class BetParticipation(db.Model):
    __tablename__ = 'bet_participation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to user
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), nullable=False)  # Link to bet
    option = db.Column(db.String(100), nullable=False)  # Selected option
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)  # Bet placement time

    def __repr__(self):
        return f"<BetParticipation User {self.user_id} Bet {self.bet_id} Option {self.option}>"

class BetResult(db.Model):
    __tablename__ = 'bet_results'
    id = db.Column(db.Integer, primary_key=True)
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), unique=True, nullable=False)  # Link to bet
    result = db.Column(db.String(100), nullable=False)  # Winning option
    declared_at = db.Column(db.DateTime, default=datetime.utcnow)  # Result declaration time

    def __repr__(self):
        return f"<BetResult Bet {self.bet_id} Result {self.result}>"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # Username for the user
    email = db.Column(db.String(120), unique=True, nullable=False)  # User email
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    participations = db.relationship('BetParticipation', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
