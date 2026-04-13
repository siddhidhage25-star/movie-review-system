"""
Routes module for the Movie Review System
Contains all application routes organized by flow:
1. Authentication (Login/Register)
2. User Flow (Browse → View Details → Add Review → Display)
3. Admin Flow (Dashboard → Analytics → Management)
4. API Endpoints
"""

from app import app
from extensions import db
from models import User, Movie, Review, LoginActivity
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user and admin login."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
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
            
            # Redirect based on role
            if current_user.role == 'admin':
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
        if User.query.filter_by(email=email).first():
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


@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ============================================================================
# USER FLOW: Browse → View Details → Add Review → Display
# ============================================================================

@app.route('/')
def index():
    """Home page - Browse all movies sorted by rating."""
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    return render_template('index.html', movies=movies)


@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    """View movie details and all reviews."""
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()
    return render_template('movie_details.html', movie=movie, reviews=reviews)


@app.route('/add_review/<int:movie_id>', methods=['POST'])
@login_required
def add_review(movie_id):
    """Add a new review for a movie."""
    movie = Movie.query.get_or_404(movie_id)
    
    rating = request.form.get('rating')
    review_text = request.form.get('review', '').strip()
    
    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5', 'danger')
            return redirect(url_for('movie_details', movie_id=movie_id))
    except (TypeError, ValueError):
        flash('Invalid rating value', 'danger')
        return redirect(url_for('movie_details', movie_id=movie_id))
    
    # Create new review
    new_review = Review(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=rating,
        review_text=review_text
    )
    db.session.add(new_review)
    
    # Update movie's average rating
    update_movie_rating(movie_id)
    
    db.session.commit()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('movie_details', movie_id=movie_id))


# ============================================================================
# ADMIN FLOW: Dashboard → Analytics → Management
# ============================================================================

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with analytics and management."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Analytics
    total_users = User.query.count()
    total_movies = Movie.query.count()
    total_reviews = Review.query.count()
    total_logins = LoginActivity.query.count()
    
    # Recent activity
    recent_logins = LoginActivity.query.order_by(LoginActivity.login_time.desc()).limit(10).all()
    
    # Management data
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


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)."""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
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


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/movies', methods=['GET'])
def api_get_movies():
    """API: Get all movies."""
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
    """API: Get movie with reviews."""
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
    """API: Search movies by title or genre."""
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


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def update_movie_rating(movie_id):
    """Recalculate average rating for a movie."""
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


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
