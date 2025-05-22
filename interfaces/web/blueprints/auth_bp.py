from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from core.database.postgres.models.user import User
from core.database.postgres.database import db
from core.common.auth import create_token
import re

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle POST request
    data = request.form
    
    # Validate required fields
    required = ['email', 'password', 'confirm_password', 'first_name']
    if not all(field in data for field in required):
        flash('All fields are required', 'error')
        return redirect(url_for('auth.signup'))
    
    # Check password match
    if data['password'] != data['confirm_password']:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth.signup'))
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        flash('Invalid email format', 'error')
        return redirect(url_for('auth.signup'))
    
    # Validate password strength
    if len(data['password']) < 8:
        flash('Password must be at least 8 characters long', 'error')
        return redirect(url_for('auth.signup'))
    
    if not any(c.isupper() for c in data['password']):
        flash('Password must contain at least one uppercase letter', 'error')
        return redirect(url_for('auth.signup'))
    
    if not any(c.islower() for c in data['password']):
        flash('Password must contain at least one lowercase letter', 'error')
        return redirect(url_for('auth.signup'))
    
    if not any(c.isdigit() for c in data['password']):
        flash('Password must contain at least one number', 'error')
        return redirect(url_for('auth.signup'))
    
    if not any(c in '!@#$%^&*(),.?":{}|<>' for c in data['password']):
        flash('Password must contain at least one special character', 'error')
        return redirect(url_for('auth.signup'))
    
    # Check if user already exists
    if User.query.filter_by(email=data['email'].lower()).first():
        flash('Email already registered', 'error')
        return redirect(url_for('auth.signup'))
    
    try:
        # Create new user
        user = User(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name']
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        # Create JWT token
        token = create_token(user.id)
        session['jwt_token'] = token
        
        flash('Successfully registered! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during registration', 'error')
        return redirect(url_for('auth.signup'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    if not data or not data.get('email') or not data.get('password'):
        flash('Email and password are required', 'error')
        return redirect(url_for('auth.login'))
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        flash('Invalid email format', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if not user or not user.check_password(data['password']):
        flash('Invalid email or password', 'error')
        return redirect(url_for('auth.login'))
    
    if not user.is_active:
        flash('Account is deactivated', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Log the user in
        login_user(user, remember=True)
        
        # Create JWT token
        token = create_token(user.id)
        
        # If API request, return token
        if request.is_json:
            return jsonify({
                'token': token,
                'user': user.to_dict()
            })
        
        # Store token in session for web interface
        session['jwt_token'] = token
        
        # Get the next page from query parameters or default to home
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.home')
        
        flash('Successfully logged in!', 'success')
        return redirect(next_page)
        
    except Exception as e:
        flash('An error occurred during login', 'error')
        return redirect(url_for('auth.login'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('jwt_token', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('main.index'))
