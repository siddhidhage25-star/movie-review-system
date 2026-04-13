# 🎬 MovieVerse

A Flask-based web application for browsing, rating, and reviewing movies with user authentication, watchlist management, and admin panel.

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Important: How to Run](#important-how-to-run)
- [Movies Database](#movies-database)
- [Project Structure](#project-structure)
- [User Guide](#user-guide)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### 👤 User Features
- ✅ User registration and authentication
- ✅ Browse 25 movies with real poster images
- ✅ Watch YouTube trailers
- ✅ Add movies to personal watchlist
- ✅ Write reviews and rate movies (1-5 stars)
- ✅ Search movies by title or genre
- ✅ Browse movies by category/genre
- ✅ Responsive design (mobile-friendly)

### 🔧 Admin Features
- ✅ Admin dashboard with analytics
- ✅ Add/edit/delete movies
- ✅ Manage users and roles
- ✅ View system statistics
- ✅ Monitor user activity

### 🎨 Technical Features
- ✅ Flask backend with PostgreSQL/SQLite
- ✅ Jinja2 template engine
- ✅ Password hashing (security)
- ✅ Session management
- ✅ Database migrations
- ✅ RESTful API endpoints

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (optional, SQLite works too)
- Modern web browser (Chrome/Edge recommended)

### Installation & Running

#### Option 1: One-Click Start
```bash
# Double-click this file:
step 1-cd movie/backend
```

#### Option 2: Command Line
```bash
# Navigate to backend folder
cd "C:\Users\Kapil\Downloads\MOVIE REVIEW SYSTEM\backend"

# Install dependencies (first time only)
already install skip-pip install -r requirements.txt

# Run the application
step 2-python app.py
```

### Access the App
Open your browser and visit: **http://localhost:5000**

### Default Login Credentials

**Admin Account:**
- Email: `admin@system.com`
- Password: `admin123`

**User Account:**
- Register a new account at: http://localhost:5000/register

---

## ⚠️ IMPORTANT: How to Run

### ❌ WRONG (Don't Do This)
- Opening HTML files with Live Server
- Double-clicking HTML files in frontend folder
- Accessing via port 5500

**Result:** You'll see raw Jinja code instead of rendered pages

### ✅ CORRECT (Do This)
1. Run Flask: `python app.py` in backend folder
2. Access via: `http://localhost:5000`
3. That's it!

### Why?
This application uses **Jinja2 templates** which require **server-side processing** by Flask. Live Server only serves static files and cannot process template syntax.

**Read these guides for detailed explanation:**
- 📖 [`QUICK_START.md`](QUICK_START.md) - Step-by-step running guide
- 🎓 [`UNDERSTANDING_FLASK.md`](UNDERSTANDING_FLASK.md) - Templates explained
- 📚 [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md) - Complete documentation

---

## 🎬 Movies Database

The app comes pre-loaded with **25 movies**:

### 🇮🇳 Bollywood (15 Movies)
1. Pushpa 2: The Rule
2. Stree 2
3. Singham Again
4. Jawan
5. Pathaan
6. Animal
7. Tiger 3
8. Fighter
9. Crew
10. Munjya
11. Shaitaan
12. Article 370
13. Bad Newz
14. Kill
15. Srikanth

### 🇺🇸 Hollywood (10 Trending Movies)
1. Deadpool & Wolverine
2. Dune: Part Two
3. Oppenheimer
4. The Batman
5. Spider-Man: Across the Spider-Verse
6. Barbie
7. Guardians of the Galaxy Vol. 3
8. John Wick: Chapter 4
9. Avatar: The Way of Water
10. Inside Out 2

**All movies include:**
- Real poster images from IMDb
- YouTube trailer
- Genre classifications
- Ratings
- Detailed descriptions

---

## 📂 Project Structure

```
MOVIE REVIEW SYSTEM/
│
├── backend/                          # Flask backend
│   ├── app.py                       # Main application
│   ├── models.py                    # Database models
│   ├── routes.py                    # URL routes (optional)
│   ├── extensions.py                # Flask extensions
│   ├── utils.py                     # Helper functions
│   ├── seed_data.py                 # Sample data seeder
│   ├── migrate_db.py                # Database migration
│   ├── setup_db.py                  # Database setup
│   ├── .env                         # Environment variables
│   └── moviereview.db               # SQLite database (if used)
│
├── frontend/                         # Jinja templates
│   ├── base.html                    # Base template
│   ├── index.html                   # Home page
│   ├── login.html                   # Login page
│   ├── register.html                # Registration page
│   ├── movies.html                  # All movies page
│   ├── movie_details.html           # Movie details + reviews
│   ├── categories.html              # Categories page
│   ├── watchlist.html               # User watchlist
│   ├── trailer.html                 # Trailer player
│   └── admin_dashboard.html         # Admin panel
│
├── static/                           # Static files
│   ├── css/
│   │   └── style.css                # Main stylesheet
│   ├── js/                          # JavaScript files
│   └── images/                      # Uploaded images
│
├── start_backend.bat                 # Windows startup script
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 📖 User Guide

### For Regular Users

1. **Register an Account**
   - Visit http://localhost:5000/register
   - Fill in your details
   - Click Register

2. **Login**
   - Visit http://localhost:5000/login
   - Enter your credentials
   - Click Login

3. **Browse Movies**
   - Click "Movies" in navbar
   - Browse all 25 movies with posters
   - Click any movie to see details

4. **Watch Trailers**
   - Open any movie details page
   - Click "Watch Trailer" button
   - YouTube trailer plays in embedded player

5. **Add to Watchlist**
   - Click "Add to Watchlist" on movie page
   - View your watchlist via bookmark icon in navbar

6. **Write Reviews**
   - Open movie details page
   - Fill in rating (1-5 stars)
   - Write your review
   - Click Submit

### For Admins

1. **Login as Admin**
   - Email: `admin@system.com`
   - Password: `admin123`

2. **Access Admin Panel**
   - Click "Admin Panel" in navbar
   - View dashboard with statistics

3. **Manage Movies**
   - Add new movies with posters and trailers
   - Edit existing movies
   - Delete movies

4. **Manage Users**
   - View all registered users
   - Change user roles
   - Delete users

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`QUICK_START.md`](QUICK_START.md) | Quick start guide with step-by-step instructions |
| [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md) | Complete documentation covering all aspects |
| [`UNDERSTANDING_FLASK.md`](UNDERSTANDING_FLASK.md) | Beginner-friendly explanation of Flask and Jinja |
| [`HOW_TO_RUN.md`](HOW_TO_RUN.md) | Detailed running instructions |
| [`SETUP_COMPLETE.md`](SETUP_COMPLETE.md) | Setup completion details |

---

## 🛠️ Troubleshooting

### Common Issues

#### Problem: Seeing Jinja code in browser
**Cause:** Using Live Server instead of Flask  
**Solution:**
```bash
run backend

cd movie/backend
python app.py

# Access: http://localhost:5000
```

#### Problem: CSS not loading
**Cause:** Accessing via wrong URL  
**Solution:** Use `http://localhost:5000` (Flask), NOT port 5500 (Live Server)

#### Problem: Database errors
**Cause:** Missing database tables  
**Solution:**
```bash
cd backend
python migrate_db.py
python seed_data.py
```

#### Problem: "Template not found"
**Cause:** Flask can't find templates folder  
**Solution:** Ensure `frontend/` folder exists with HTML files

#### Problem: Movies don't have images
**Cause:** Old database without poster URLs  
**Solution:**
```bash
# In Python or command line:
cd backend
python -c "from app import app; from extensions import db; from models import Movie; app.app_context().push(); Movie.query.delete(); db.session.commit()"
python seed_data.py
```

---

## 🔧 Configuration

### Environment Variables (`.env` file)

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/moviereviewdb
# Or use SQLite:
# DATABASE_URL=sqlite:///moviereview.db

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

### Database Options

**PostgreSQL (Default):**
- Requires PostgreSQL installed and running
- Create database: `CREATE DATABASE moviereviewdb;`
- Update `.env` with your credentials

**SQLite (Alternative):**
- No setup required
- Database file created automatically
- Change `DATABASE_URL` in `.env` to: `sqlite:///moviereview.db`

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.1
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 🌐 API Endpoints

The application provides REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/movies` | GET | Get all movies |
| `/api/movies/<id>` | GET | Get movie by ID |
| `/api/search?q=query` | GET | Search movies |

---

## 🔒 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Session management with Flask-Login
- ✅ CSRF protection
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Role-based access control

---

## 🎨 UI/UX Features

- ✅ Netflix-inspired dark theme
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Smooth animations and transitions
- ✅ Glass morphism effects
- ✅ Hover effects on movie cards
- ✅ Star rating system
- ✅ Embedded YouTube trailer player

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💻 Developer

Built with ❤️ using Flask, PostgreSQL, and Jinja2

---

## 🆘 Need Help?

1. Check the documentation files in this repository
2. Review the troubleshooting section
3. Check Flask terminal for error messages
4. Ensure all dependencies are installed

---

## 🎯 Quick Reference

| What | How |
|------|-----|
| **Run app** | `cd backend && python app.py` |
| **Access app** | http://localhost:5000 |
| **Admin login** | admin@system.com / admin123 |
| **Reset database** | `python migrate_db.py && python seed_data.py` |
| **Stop server** | Press `Ctrl+C` in terminal |
| **View docs** | Read `.md` files in project root |

---

**Enjoy browsing and reviewing movies! 🎬🍿**
