from flask import Flask, request, jsonify, render_template
from models import db, bcrypt, User
from config import Config
from datetime import datetime, timedelta
import os

def create_app(config_class=Config):
    """
    Factory function to create the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Folder already exists

    # Force the DATABASE_URI to use the app's absolute instance_path
    # This overrides the relative path (or default) from the config.
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "app.db")}'

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        # This will now work
        db.create_all()

    # FRONTEND PAGE ROUTE
    # These routes just render the HTML pages.

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/reset')
    def reset_page():
        return render_template('reset.html')

    @app.route('/users')
    def users_page():
        return render_template('users.html')


    # BACKEND API ROUTES
    # These routes handle data (JSON) and logic.
    
    @app.route('/api/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409

        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': f'User {username} registered successfully'}), 201

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()

        if user and user.is_locked():
            return jsonify({
                'error': 'Account locked. Try again later.',
                'locked_until': user.lockout_until.isoformat()
            }), 403

        if not user or not user.check_password(password):
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= app.config['LOCKOUT_ATTEMPTS']:
                    user.lockout_until = datetime.utcnow() + timedelta(
                        minutes=app.config['LOCKOUT_DURATION_MINUTES']
                    )
                    db.session.commit()
                    return jsonify({'error': 'Account locked due to too many failed attempts'}), 403
                
                db.session.commit()

            return jsonify({'error': 'Invalid credentials'}), 401

        user.failed_login_attempts = 0
        user.lockout_until = None
        db.session.commit()

        return jsonify({'message': 'Login successful'}), 200

    @app.route('/api/users', methods=['GET'])
    def api_get_users():
        """(For testing) Lists all registered users."""
        users = User.query.all()
        user_list = [
            {
                'id': u.id,
                'username': u.username,
                'failed_attempts': u.failed_login_attempts,
                'locked_out': u.is_locked()
            } for u in users
        ]
        return jsonify(user_list), 200

    @app.route('/api/reset', methods=['POST'])
    def api_reset_password():
        data = request.get_json()
        username = data.get('username')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not all([username, old_password, new_password]):
            return jsonify({'error': 'Username, old_password, and new_password are required'}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(old_password):
            return jsonify({'error': 'Invalid username or old password'}), 401

        if user.is_locked():
            return jsonify({'error': 'Account is locked, cannot reset password right now'}), 403

        user.set_password(new_password)
        user.failed_login_attempts = 0
        user.lockout_until = None
        db.session.commit()

        return jsonify({'message': 'Password reset successful'}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
