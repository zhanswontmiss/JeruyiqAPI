from flask import Flask, jsonify, render_template
from config.config import Config
from core.database.postgres.database import init_db, db
from core.database.firebase.firebase_client import init_firebase
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from core.database.postgres.models.user import User
from core.database.postgres.models.property import Property
from core.database.postgres.models.booking import Booking

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='interfaces/web/templates', static_folder='interfaces/web/static')
    app.config.from_object(config_class)

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize database
    init_db(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Create tables within app context if they don't exist
    with app.app_context():
        db.create_all()

    # Temporarily disable Firebase
    # init_firebase(app)    # Register API blueprints
    from interfaces.api.v1 import booking_routes, property_routes, tour_routes
    from interfaces.api.v1 import attraction_routes, user_routes, guide_routes, visa_routes, ai_routes
    app.register_blueprint(booking_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(property_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(tour_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(attraction_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(user_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(guide_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(visa_routes.bp, url_prefix='/api/v1')
    app.register_blueprint(ai_routes.bp, url_prefix='/api/v1')

    # Register web blueprints
    from interfaces.web.blueprints.auth_bp import bp as auth_bp
    from interfaces.web.blueprints.main_bp import bp as main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
