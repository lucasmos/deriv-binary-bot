from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from .forms import LoginForm, RegistrationForm, ResetPasswordForm, BrokerLinkForm
from .models import User
from .services.email_service import send_verification_email, send_password_reset_email
from .services.oauth_service import setup_google_oauth
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            demo_balance=10000.00
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        send_verification_email(user)
        flash('Congratulations, you are now registered! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html', title='Register', form=form)

@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('main.index'))
    
    if user.is_verified:
        flash('Account already verified.', 'info')
    else:
        user.is_verified = True
        db.session.commit()
        flash('Thank you for verifying your email!', 'success')
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired password reset link', 'danger')
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/link_broker', methods=['GET', 'POST'])
@login_required
def link_broker():
    form = BrokerLinkForm()
    if form.validate_on_submit():
        try:
            credentials = {
                'api_key': form.api_key.data,
                'account_id': form.account_id.data
            }
            current_user.link_broker_account(form.broker_name.data, credentials)
            flash(f"{form.broker_name.data} account linked successfully!", 'success')
            return redirect(url_for('user.settings'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('auth/link_broker.html', form=form)

# Google OAuth Routes
google_bp = setup_google_oauth()
auth_bp.register_blueprint(google_bp, url_prefix='/google')