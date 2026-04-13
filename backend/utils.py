"""
Utility functions for the Movie Review System
Helper functions for common operations.
"""

from extensions import db
from models import Movie, Review
from datetime import datetime


def update_movie_rating(movie_id):
    """
    Recalculate average rating for a movie based on all reviews.
    
    Args:
        movie_id (int): ID of the movie
        
    Returns:
        float: New average rating (0.0 if no reviews)
    """
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    if reviews:
        total_rating = sum(r.rating for r in reviews)
        avg_rating = round(total_rating / len(reviews), 1)
        movie = Movie.query.get(movie_id)
        if movie:
            movie.rating = avg_rating
            db.session.commit()
        return avg_rating
    return 0.0


def format_datetime(dt):
    """
    Format datetime object to readable string.
    
    Args:
        dt (datetime): Datetime object
        
    Returns:
        str: Formatted date string (e.g., "April 04, 2026")
    """
    if dt:
        return dt.strftime('%B %d, %Y at %I:%M %p')
    return 'N/A'


def get_movie_stats(movie_id):
    """
    Get statistics for a movie.
    
    Args:
        movie_id (int): ID of the movie
        
    Returns:
        dict: Movie statistics
    """
    movie = Movie.query.get(movie_id)
    if not movie:
        return None
    
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    review_count = len(reviews)
    
    if review_count > 0:
        avg_rating = round(sum(r.rating for r in reviews) / review_count, 1)
        rating_distribution = {
            5: len([r for r in reviews if r.rating == 5]),
            4: len([r for r in reviews if r.rating == 4]),
            3: len([r for r in reviews if r.rating == 3]),
            2: len([r for r in reviews if r.rating == 2]),
            1: len([r for r in reviews if r.rating == 1])
        }
    else:
        avg_rating = 0.0
        rating_distribution = {i: 0 for i in range(1, 6)}
    
    return {
        'movie': movie,
        'review_count': review_count,
        'average_rating': avg_rating,
        'rating_distribution': rating_distribution
    }


def get_user_stats(user_id):
    """
    Get statistics for a user.
    
    Args:
        user_id (int): ID of the user
        
    Returns:
        dict: User statistics
    """
    from models import User, LoginActivity

    user = User.query.get(user_id)
    if not user:
        return None
    
    reviews_count = Review.query.filter_by(user_id=user_id).count()
    logins_count = LoginActivity.query.filter_by(user_id=user_id).count()
    last_login = user.last_login
    
    return {
        'user': user,
        'reviews_count': reviews_count,
        'logins_count': logins_count,
        'last_login': last_login,
        'member_since': user.created_at
    }


def search_movies(query, limit=20):
    """
    Search movies by title or genre.
    
    Args:
        query (str): Search query
        limit (int): Maximum results to return
        
    Returns:
        list: List of matching Movie objects
    """
    search_term = f'%{query}%'
    movies = Movie.query.filter(
        db.or_(
            Movie.title.ilike(search_term),
            Movie.genre.ilike(search_term),
            Movie.description.ilike(search_term)
        )
    ).order_by(Movie.rating.desc()).limit(limit).all()
    
    return movies


def get_trending_movies(limit=10):
    """
    Get trending movies (highest rated with most reviews).
    
    Args:
        limit (int): Number of movies to return
        
    Returns:
        list: List of trending Movie objects
    """
    movies = Movie.query.order_by(Movie.rating.desc()).limit(limit).all()
    return movies


def get_recent_reviews(limit=10):
    """
    Get most recent reviews.
    
    Args:
        limit (int): Number of reviews to return
        
    Returns:
        list: List of recent Review objects
    """
    reviews = Review.query.order_by(Review.created_at.desc()).limit(limit).all()
    return reviews


def validate_rating(rating):
    """
    Validate rating value (1-5).
    
    Args:
        rating: Rating value to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return False, 'Rating must be between 1 and 5'
        return True, None
    except (TypeError, ValueError):
        return False, 'Invalid rating value'
