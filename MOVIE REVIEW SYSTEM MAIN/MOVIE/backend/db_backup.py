import json
import os
from datetime import datetime

from app import app
from models import User, Movie, Review, Watchlist, LoginActivity

BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')


def serialize_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'password': user.password,
        'role': user.role,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }


def serialize_movie(movie):
    return {
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'release_date': movie.release_date,
        'genre': movie.genre,
        'rating': movie.rating,
        'poster_url': movie.poster_url,
        'trailer_url': movie.trailer_url,
        'created_at': movie.created_at.isoformat() if movie.created_at else None,
    }


def serialize_review(review):
    return {
        'id': review.id,
        'user_id': review.user_id,
        'movie_id': review.movie_id,
        'rating': review.rating,
        'review_text': review.review_text,
        'created_at': review.created_at.isoformat() if review.created_at else None,
    }


def serialize_watchlist(item):
    return {
        'id': item.id,
        'user_id': item.user_id,
        'movie_id': item.movie_id,
        'added_at': item.added_at.isoformat() if item.added_at else None,
    }


def serialize_login_activity(entry):
    return {
        'id': entry.id,
        'user_id': entry.user_id,
        'login_time': entry.login_time.isoformat() if entry.login_time else None,
    }


def backup_database():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'db_backup_{timestamp}.json')

    with app.app_context():
        data = {
            'users': [serialize_user(u) for u in User.query.order_by(User.id).all()],
            'movies': [serialize_movie(m) for m in Movie.query.order_by(Movie.id).all()],
            'reviews': [serialize_review(r) for r in Review.query.order_by(Review.id).all()],
            'watchlists': [serialize_watchlist(w) for w in Watchlist.query.order_by(Watchlist.id).all()],
            'login_activity': [serialize_login_activity(a) for a in LoginActivity.query.order_by(LoginActivity.id).all()],
        }

    with open(backup_path, 'w', encoding='utf-8') as backup_file:
        json.dump(data, backup_file, indent=2, ensure_ascii=False)

    print(f'Database backup saved to: {backup_path}')


if __name__ == '__main__':
    backup_database()
