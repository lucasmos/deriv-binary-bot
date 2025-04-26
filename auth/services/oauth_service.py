from flask import redirect, url_for, flash
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import login_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from .models import User, db

def setup_google_oauth():
    google_bp = make_google_blueprint(
        client_id=current_app.config['GOOGLE_CLIENT_ID'],
        client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
        scope=['profile', 'email'],
        redirect_to='auth.google_login'
    )
    
    @oauth_authorized.connect_via(google_bp)
    def google_logged_in(blueprint, token):
        if not token:
            flash("Failed to log in with Google.", category="error")
            return False
        
        resp = blueprint.session.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", category="error")
            return False
        
        google_info = resp.json()
        google_user_id = google_info["id"]
        email = google_info["email"]
        
        # Find this OAuth token in the database, or create it
        query = User.query.filter_by(email=email)
        try:
            user = query.one()
        except NoResultFound:
            # Create a new user
            user = User(
                username=email.split('@')[0],
                email=email,
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
        
        # Log in the user
        login_user(user)
        flash("Successfully signed in with Google.", "success")
        
        # Disable Flask-Dance's default behavior for saving the OAuth token
        return False
    
    @oauth_error.connect_via(google_bp)
    def google_error(blueprint, error, error_description=None, error_uri=None):
        msg = (
            "OAuth error from {name}! "
            "error={error} description={description} uri={uri}"
        ).format(
            name=blueprint.name,
            error=error,
            description=error_description,
            uri=error_uri,
        )
        flash(msg, category="error")
    
    return google_bp