#!/usr/bin/env python3
from deriv import create_app, db
from deriv.models import User, Role

def setup_database():
    app = create_app()
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create default roles
        roles = ['user', 'creator', 'admin']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Assign admin role
            admin_role = Role.query.filter_by(name='admin').first()
            admin.roles.append(admin_role)
        
        db.session.commit()
        print("Database setup complete")

if __name__ == '__main__':
    setup_database()