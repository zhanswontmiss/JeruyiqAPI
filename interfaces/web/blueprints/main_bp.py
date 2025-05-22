from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from core.database.postgres.database import db

bp = Blueprint('main', __name__)

@bp.route('/home')
@login_required
def home():
    return render_template('main.html')

@bp.route('/')
@bp.route('/getstarted')
def index():
    return render_template('startpage.html')

@bp.route('/signup')
def signup():
    return render_template('signup.html')

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'GET':
        return render_template('user/edit_profile.html', user=current_user)
    
    data = request.form
    
    # Update allowed fields
    if data.get('first_name'):
        current_user.first_name = data['first_name']
        
    # Handle password change
    if data.get('new_password'):
        if not data.get('current_password'):
            flash('Current password is required', 'error')
            return redirect(url_for('main.edit_profile'))
            
        if not current_user.check_password(data['current_password']):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('main.edit_profile'))
            
        current_user.set_password(data['new_password'])
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))
