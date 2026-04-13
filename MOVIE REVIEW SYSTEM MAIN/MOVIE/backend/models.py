"""
Database Models for Movie Review System
Defines the database schema for users, movies, reviews, and login activity.
"""

from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    login_activities = db.relationship('LoginActivity', backref='user', lazy=True, cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name} ({self.email or "No Email"})>'
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'


class Movie(db.Model):
    """Movie model for storing movie information."""
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    release_date = db.Column(db.String(20))
    genre = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    poster_url = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade='all, delete-orphan')
    watchlists = db.relationship('Watchlist', backref='movie', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Movie {self.title}>'

    def get_review_count(self):
        """Get the total number of reviews for this movie."""
        return Review.query.filter_by(movie_id=self.id).count()

    def get_average_rating(self):
        """Calculate and return the average rating from reviews."""
        reviews = Review.query.filter_by(movie_id=self.id).all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 1)
        return 0.0


class Review(db.Model):
    """Review model for user movie reviews and ratings."""
    __tablename__ = 'reviews'
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_review'),)
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review by User {self.user_id} for Movie {self.movie_id}>'
    
    def get_star_display(self):
        """Return filled and empty stars for display."""
        filled_stars = '★' * self.rating
        empty_stars = '☆' * (5 - self.rating)
        return filled_stars + empty_stars


class LoginActivity(db.Model):
    """Login activity model for tracking user logins."""
    __tablename__ = 'login_activity'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LoginActivity User {self.user_id} at {self.login_time}>'


class Watchlist(db.Model):
    """Watchlist model for users to save movies they want to watch."""
    __tablename__ = 'watchlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate entries
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watchlist'),)

    def __repr__(self):
        return f'<Watchlist User {self.user_id} Movie {self.movie_id}>'
