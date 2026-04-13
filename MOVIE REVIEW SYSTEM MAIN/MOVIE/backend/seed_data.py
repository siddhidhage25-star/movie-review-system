"""Seed the configured database with only the selected movie set."""

from app import app
from extensions import db
from models import User, Movie, Review, Watchlist, LoginActivity
from werkzeug.security import generate_password_hash

MOVIES = [
    {
        'title': 'The Batman',
        'description': 'A dark detective thriller with gritty action and intense atmosphere.',
        'release_date': '2022',
        'genre': 'Action, Crime',
        'poster_url': '/static/images/posters/the_batman.jpg',
        'trailer_url': 'https://www.youtube.com/embed/mqqft2x_Aa4',
        'rating': 8.2
    },
    {
        'title': 'Dune: Part Two',
        'description': 'Epic science-fiction drama with breathtaking visuals and sweeping scale.',
        'release_date': '2024',
        'genre': 'Sci-Fi, Adventure',
        'poster_url': '/static/images/posters/dune_part_two.jpg',
        'trailer_url': 'https://www.youtube.com/embed/Way9Dexny3w',
        'rating': 8.6
    },
    {
        'title': 'Oppenheimer',
        'description': 'A historical biopic that explores ambition, consequence, and moral conflict.',
        'release_date': '2023',
        'genre': 'Drama, History',
        'poster_url': '/static/images/posters/oppenheimer.jpg',
        'trailer_url': 'https://www.youtube.com/embed/uYPbbksJxIg',
        'rating': 8.4
    },
    {
        'title': 'Spider-Man: Across the Spider-Verse',
        'description': 'A visually stunning animated adventure with heart and humor.',
        'release_date': '2023',
        'genre': 'Animation, Action',
        'poster_url': '/static/images/posters/spider-man_across_the_spider-verse.jpg',
        'trailer_url': 'https://www.youtube.com/embed/cqGjhVJWtEg',
        'rating': 8.9
    },
    {
        'title': 'Guardians of the Galaxy Vol. 3',
        'description': 'A heartfelt space opera with humor, action, and emotional stakes.',
        'release_date': '2023',
        'genre': 'Action, Sci-Fi',
        'poster_url': '/static/images/posters/guardians_of_the_galaxy_vol_3.jpg',
        'trailer_url': 'https://www.youtube.com/embed/u3V5KDHRQvk',
        'rating': 8.1
    },
    {
        'title': 'Deadpool & Wolverine',
        'description': 'A wild superhero adventure packed with irreverent humor and action.',
        'release_date': '2024',
        'genre': 'Action, Comedy',
        'poster_url': '/static/images/posters/deadpool_and_wolverine.jpg',
        'trailer_url': 'https://www.youtube.com/embed/73_1biulkYk',
        'rating': 8.5
    },
    {
        'title': 'John Wick: Chapter 4',
        'description': 'A stylish action thriller built on precise fight choreography and momentum.',
        'release_date': '2023',
        'genre': 'Action, Thriller',
        'poster_url': '/static/images/posters/john_wick_chapter_4.jpg',
        'trailer_url': 'https://www.youtube.com/embed/qEVUtrk8_B4',
        'rating': 8.3
    },
    {
        'title': 'Avatar: The Way of Water',
        'description': 'A visually immersive sci-fi adventure with oceanic wonder and drama.',
        'release_date': '2022',
        'genre': 'Sci-Fi, Adventure',
        'poster_url': '/static/images/posters/avatar_the_way_of_water.jpg',
        'trailer_url': 'https://www.youtube.com/embed/d9MyW72ELq0',
        'rating': 7.8
    },
    {
        'title': 'Inside Out 2',
        'description': 'A heartfelt animated film that brings new emotions and family moments to life.',
        'release_date': '2024',
        'genre': 'Animation, Family',
        'poster_url': '/static/images/posters/inside_out_2.jpg',
        'trailer_url': 'https://www.youtube.com/embed/LEjhY15eCx0',
        'rating': 7.9
    }
]

REVIEWS = [
    {
        'movie_title': 'Dune: Part Two',
        'rating': 5,
        'review_text': 'Epic storytelling with stunning visuals and world-building.'
    },
    {
        'movie_title': 'Deadpool & Wolverine',
        'rating': 4,
        'review_text': 'Fun and chaotic superhero entertainment with great humor.'
    },
    {
        'movie_title': 'Spider-Man: Across the Spider-Verse',
        'rating': 5,
        'review_text': 'One of the best animated films with incredible style and heart.'
    }
]


def create_admin_user():
    admin_email = 'admin@system.com'
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            name='Admin User',
            email=admin_email,
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Created admin user')
    return admin


def create_default_users():
    users = {}
    users['admin'] = create_admin_user()

    guest_email = 'guest@guest.com'
    guest = User.query.filter_by(email=guest_email).first()
    if not guest:
        guest = User(
            name='Guest User',
            email=guest_email,
            password=generate_password_hash('guest'),
            role='user'
        )
        db.session.add(guest)
        db.session.commit()
        print('Created guest user')
    users['guest'] = guest

    regular_email = 'siddhidhage25@gmail.com'
    regular = User.query.filter_by(email=regular_email).first()
    if not regular:
        regular = User(
            name='Siddhi Hage',
            email=regular_email,
            password=generate_password_hash('siddhi1234'),
            role='user'
        )
        db.session.add(regular)
        db.session.commit()
        print('Created regular user')
    users['regular'] = regular

    # Remove any old user records with mistyped email addresses
    typo_user = User.query.filter_by(email='siddhidage25@gmail.com').first()
    if typo_user:
        db.session.delete(typo_user)
        db.session.commit()
        print('Removed outdated user account with incorrect email')

    return users


def seed_login_activity(users):
    entries = []
    if users.get('guest'):
        entries.append(LoginActivity(user_id=users['guest'].id))
    if users.get('regular'):
        entries.append(LoginActivity(user_id=users['regular'].id))
    if entries:
        db.session.bulk_save_objects(entries)
        db.session.commit()
        print(f'Seeded {len(entries)} login activity records')


def seed_watchlists(users):
    watchlist_pairs = [
        ('guest', 'The Batman'),
        ('guest', 'Spider-Man: Across the Spider-Verse'),
        ('regular', 'Dune: Part Two'),
        ('regular', 'Oppenheimer'),
        ('regular', 'John Wick: Chapter 4')
    ]

    added = 0
    for user_key, movie_title in watchlist_pairs:
        user = users.get(user_key)
        movie = Movie.query.filter_by(title=movie_title).first()
        if not user or not movie:
            continue
        if not Watchlist.query.filter_by(user_id=user.id, movie_id=movie.id).first():
            db.session.add(Watchlist(user_id=user.id, movie_id=movie.id))
            added += 1

    if added:
        db.session.commit()
    print(f'Seeded {added} watchlist entries')


def clear_movies():
    deleted_reviews = Review.query.delete()
    deleted_watchlist = Watchlist.query.delete()
    deleted_login = LoginActivity.query.delete()
    deleted_movies = Movie.query.delete()
    db.session.commit()
    print(f'Removed {deleted_movies} movies, {deleted_reviews} reviews, {deleted_watchlist} watchlist entries, and {deleted_login} login activity records')


def seed_movies():
    added_count = 0
    for movie_data in MOVIES:
        movie = Movie(
            title=movie_data['title'],
            description=movie_data['description'],
            release_date=movie_data['release_date'],
            genre=movie_data['genre'],
            poster_url=movie_data['poster_url'],
            trailer_url=movie_data['trailer_url'],
            rating=movie_data['rating']
        )
        db.session.add(movie)
        added_count += 1
    db.session.commit()
    print(f'Seeded {added_count} movies')


def seed_reviews(admin_user):
    added_count = 0
    for review_data in REVIEWS:
        movie = Movie.query.filter_by(title=review_data['movie_title']).first()
        if not movie:
            continue
        review = Review(
            user_id=admin_user.id,
            movie_id=movie.id,
            rating=review_data['rating'],
            review_text=review_data['review_text']
        )
        db.session.add(review)
        added_count += 1
    db.session.commit()
    print(f'Seeded {added_count} sample reviews')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        users = create_default_users()
        clear_movies()
        seed_movies()
        seed_reviews(users['admin'])
        seed_login_activity(users)
        seed_watchlists(users)

        print('Final counts:')
        print(' Users:', User.query.count())
        print(' Movies:', Movie.query.count())
        print(' Reviews:', Review.query.count())
        print(' Watchlist entries:', Watchlist.query.count())
        print(' Login activity records:', LoginActivity.query.count())
