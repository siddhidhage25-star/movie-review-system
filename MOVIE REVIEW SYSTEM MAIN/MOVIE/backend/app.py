from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import re
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from extensions import db, login_manager

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)


def get_youtube_embed_url(url):
    if not url:
        return ''

    url = url.strip()
    parsed = urlparse(url)
    hostname = (parsed.hostname or '').lower()
    video_id = ''

    if hostname.endswith('youtu.be'):
        video_id = parsed.path.lstrip('/')
    elif 'youtube.com' in hostname or 'youtube-nocookie.com' in hostname:
        if parsed.path.startswith('/embed/'):
            existing_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else ''
            if existing_id:
                return f'https://www.youtube-nocookie.com/embed/{existing_id}'
            return url
        if parsed.path.startswith('/watch'):
            query = parse_qs(parsed.query)
            video_id = query.get('v', [''])[0]
        elif parsed.path.startswith('/shorts/'):
            video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else ''
        elif parsed.path.startswith('/v/'):
            video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else ''
        else:
            match = re.search(r'(?:embed/|v/|watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
            if match:
                video_id = match.group(1)
    else:
        return url

    if video_id:
        return f'https://www.youtube-nocookie.com/embed/{video_id}'

    return url


# Initialize Flask app
app = Flask(__name__, template_folder='../frontend', static_folder='../static')

# Configuration from .env
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///movieverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'images')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Expose YouTube embed helper in templates
app.jinja_env.globals['youtube_embed_url'] = get_youtube_embed_url

# Import models after db initialization
from models import User, Movie, Review, LoginActivity, Watchlist


# --- User Loader for Flask-Login ---

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Helper Functions ---

def update_movie_rating(movie_id, commit=True):
    """Recalculate average rating for a movie based on all reviews."""
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    avg_rating = 0.0
    if reviews:
        total_rating = sum(r.rating for r in reviews)
        avg_rating = round(total_rating / len(reviews), 1)

    movie = Movie.query.get(movie_id)
    if movie:
        movie.rating = avg_rating
        if commit:
            db.session.commit()

    return avg_rating


# --- Routes ---

@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/movies')
@login_required
def movies_list():
    movies = Movie.query.all()
    return render_template('movies.html', movies=movies)


@app.route('/categories')
def categories_page():
    """Categories page - requires login."""
    if not current_user.is_authenticated:
        flash('Please login to browse categories.', 'info')
        return redirect(url_for('login'))
    
    # Get all unique genres and count movies per genre
    all_movies = Movie.query.all()
    genres = {}
    for movie in all_movies:
        if movie.genre:
            genre_list = [g.strip() for g in movie.genre.split(',')]
            for genre in genre_list:
                genres[genre] = genres.get(genre, 0) + 1
    
    return render_template('categories.html', genres=genres)


@app.route('/category/<genre_name>')
def category_movies(genre_name):
    """Show movies in a specific category."""
    if not current_user.is_authenticated:
        flash('Please login to browse categories.', 'info')
        return redirect(url_for('login'))
    
    # Convert URL-friendly name back to proper genre name
    genre_search = genre_name.replace('-', ' ')
    
    movies = Movie.query.filter(Movie.genre.ilike(f'%{genre_search}%')).order_by(Movie.rating.desc()).all()
    return render_template('movies.html', movies=movies, category=genre_search)


@app.route('/search')
def search():
    """Search movies by title or genre."""
    if not current_user.is_authenticated:
        flash('Please login to search movies.', 'info')
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('movies_list'))

    movies = Movie.query.filter(
        db.or_(
            Movie.title.ilike(f'%{query}%'),
            Movie.genre.ilike(f'%{query}%')
        )
    ).order_by(Movie.rating.desc()).all()

    return render_template('movies.html', movies=movies, query=query)


@app.route('/watchlist')
@login_required
def watchlist():
    """User's watchlist page."""
    watchlist_items = Watchlist.query.filter_by(user_id=current_user.id).all()
    movies = [Movie.query.get(item.movie_id) for item in watchlist_items]
    movies = [movie for movie in movies if movie is not None]
    return render_template('watchlist.html', movies=movies)


@app.route('/watchlist/add/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    """Add a movie to user's watchlist."""
    movie = Movie.query.get_or_404(movie_id)
    
    # Check if already in watchlist
    existing = Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if existing:
        flash('Movie already in your watchlist', 'info')
    else:
        new_watchlist = Watchlist(user_id=current_user.id, movie_id=movie_id)
        db.session.add(new_watchlist)
        db.session.commit()
        flash(f'{movie.title} added to your watchlist!', 'success')
    
    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/watchlist/remove/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_watchlist(movie_id):
    """Remove a movie from user's watchlist."""
    watchlist_item = Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first_or_404()
    db.session.delete(watchlist_item)
    db.session.commit()
    flash('Movie removed from your watchlist', 'success')
    return redirect(url_for('watchlist'))


@app.route('/movie/<int:movie_id>/trailer')
def watch_trailer(movie_id):
    """Watch movie trailer."""
    movie = Movie.query.get_or_404(movie_id)
    if not movie.trailer_url:
        flash('Trailer not available for this movie', 'info')
        return redirect(url_for('movie_details', movie_id=movie_id))

    movie.trailer_url = get_youtube_embed_url(movie.trailer_url)
    return render_template('trailer.html', movie=movie)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user and admin login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.form.get('next') or request.args.get('next')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # Update last login time
            user.last_login = datetime.utcnow()

            # Record login activity
            activity = LoginActivity(user_id=user.id)
            db.session.add(activity)
            db.session.commit()

            flash('Login successful!', 'success')

            # Redirect to the next page if provided, otherwise based on role
            if next_page:
                return redirect(next_page)

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password', '')

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/guest-login', methods=['GET'])
def guest_login():
    """Handle guest login without credentials."""
    # Check if guest user exists, create if not
    guest_user = User.query.filter_by(name='Guest User').first()
    if not guest_user:
        try:
            guest_user = User(
                name='Guest User',
                email=None,
                password=generate_password_hash('guest'),
                role='user'
            )
            db.session.add(guest_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            guest_user = User.query.filter_by(name='Guest User').first()

    # Log in the guest user
    if guest_user:
        if guest_user.email is not None:
            guest_user.email = None
            db.session.commit()
        guest_user.last_login = datetime.utcnow()
        login_user(guest_user)
        login_activity = LoginActivity(user_id=guest_user.id)
        db.session.add(login_activity)
        db.session.commit()
        flash('You are now browsing as a guest.', 'info')
    
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    """Display detailed information about a specific movie."""
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()
    return render_template('movie_details.html', movie=movie, reviews=reviews)


@app.route('/add_review/<int:movie_id>', methods=['POST'])
@login_required
def add_review(movie_id):
    """Add or update a review for a movie."""
    movie = Movie.query.get_or_404(movie_id)

    rating = request.form.get('rating')
    review_text = request.form.get('review', '').strip()

    if not review_text:
        flash('Review text cannot be empty', 'danger')
        return redirect(url_for('movie_details', movie_id=movie_id))

    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5', 'danger')
            return redirect(url_for('movie_details', movie_id=movie_id))
    except (TypeError, ValueError):
        flash('Invalid rating value', 'danger')
        return redirect(url_for('movie_details', movie_id=movie_id))

    existing_review = Review.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()

    try:
        if existing_review:
            existing_review.rating = rating
            existing_review.review_text = review_text
            flash('Review updated successfully!', 'success')
        else:
            new_review = Review(
                user_id=current_user.id,
                movie_id=movie_id,
                rating=rating,
                review_text=review_text
            )
            db.session.add(new_review)
            flash('Review added successfully!', 'success')

        update_movie_rating(movie_id, commit=False)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('An error occurred while saving your review', 'danger')

    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/db-status')
def db_status():
    return jsonify({
        'database': app.config['SQLALCHEMY_DATABASE_URI'],
        'users': User.query.count(),
        'movies': Movie.query.count(),
        'reviews': Review.query.count(),
        'watchlists': Watchlist.query.count(),
        'login_activity': LoginActivity.query.count(),
    })


@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with system statistics and management."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Get statistics
    total_users = User.query.count()
    total_movies = Movie.query.count()
    total_reviews = Review.query.count()
    total_logins = LoginActivity.query.count()
    
    # Get recent login activities
    recent_logins = LoginActivity.query.order_by(LoginActivity.login_time.desc()).limit(10).all()
    
    # Get all users and movies for management
    users = User.query.order_by(User.created_at.desc()).all()
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_movies=total_movies,
                           total_reviews=total_reviews,
                           total_logins=total_logins,
                           recent_logins=recent_logins,
                           users=users,
                           movies=movies)


# --- Admin API Routes ---

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)."""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
def update_user_role(user_id):
    """Update user role (admin only)."""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'user')
    
    if new_role not in ['user', 'admin']:
        flash('Invalid role', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Prevent admin from demoting themselves
    if user.id == current_user.id:
        flash('You cannot change your own role', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'User role updated to {new_role}', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/movie/add', methods=['GET', 'POST'])
@login_required
def add_movie():
    """Add a new movie (admin only)."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        release_date = request.form.get('release_date', '')
        genre = request.form.get('genre', '')
        poster_url = request.form.get('poster_url', '')
        
        if not title:
            flash('Movie title is required', 'danger')
            return redirect(url_for('add_movie'))
        
        new_movie = Movie(
            title=title,
            description=description,
            release_date=release_date,
            genre=genre,
            poster_url=poster_url,
            rating=0.0
        )
        db.session.add(new_movie)
        db.session.commit()
        
        flash('Movie added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_movie.html')


@app.route('/admin/movie/<int:movie_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    """Edit a movie (admin only)."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    movie = Movie.query.get_or_404(movie_id)
    
    if request.method == 'POST':
        movie.title = request.form.get('title', movie.title)
        movie.description = request.form.get('description', movie.description)
        movie.release_date = request.form.get('release_date', movie.release_date)
        movie.genre = request.form.get('genre', movie.genre)
        movie.poster_url = request.form.get('poster_url', movie.poster_url)
        
        db.session.commit()
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_movie.html', movie=movie)


@app.route('/admin/movie/<int:movie_id>/delete', methods=['POST'])
@login_required
def delete_movie(movie_id):
    """Delete a movie (admin only)."""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    movie = Movie.query.get_or_404(movie_id)
    
    try:
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting movie', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete a review (admin or review author only)."""
    review = Review.query.get_or_404(review_id)
    
    # Check if user is admin or the review author
    if current_user.role != 'admin' and review.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    movie_id = review.movie_id
    
    try:
        db.session.delete(review)
        update_movie_rating(movie_id)
        db.session.commit()
        flash('Review deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting review', 'danger')
    
    return redirect(url_for('movie_details', movie_id=movie_id))


# --- API Routes (JSON responses) ---

@app.route('/api/movies', methods=['GET'])
def api_get_movies():
    """API endpoint to get all movies."""
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    return jsonify([{
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'release_date': movie.release_date,
        'genre': movie.genre,
        'rating': movie.rating,
        'poster_url': movie.poster_url
    } for movie in movies])


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def api_get_movie(movie_id):
    """API endpoint to get a specific movie."""
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()
    
    return jsonify({
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'release_date': movie.release_date,
        'genre': movie.genre,
        'rating': movie.rating,
        'poster_url': movie.poster_url,
        'reviews': [{
            'id': review.id,
            'user_id': review.user_id,
            'username': review.author.name,
            'rating': review.rating,
            'review_text': review.review_text,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for review in reviews]
    })


@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint to search movies by title or genre."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    movies = Movie.query.filter(
        db.or_(
            Movie.title.ilike(f'%{query}%'),
            Movie.genre.ilike(f'%{query}%')
        )
    ).all()
    
    return jsonify([{
        'id': movie.id,
        'title': movie.title,
        'genre': movie.genre,
        'rating': movie.rating,
        'poster_url': movie.poster_url
    } for movie in movies])


# --- Error Handlers ---

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500


# --- Database Initialization ---

def init_db():
    """Initialize database and create tables."""
    with app.app_context():
        db.create_all()

        # Seed admin user if not exists
        if not User.query.filter_by(email='admin@system.com').first():
            admin = User(
                name='Admin User',
                email='admin@system.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('Database initialized with admin user.')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
