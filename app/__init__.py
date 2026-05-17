import os
import logging
import time
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blood_donation.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File Upload Config
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5 MB max
    
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_super_key')

    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # Swagger UI Setup
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json' # Dummy or generated file
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "VitalDrop API"})
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Basic Logging setup
    logging.basicConfig(level=logging.INFO)
    app.logger.info('Blood Donation Application startup')

    # Register blueprints/routes
    from app.routes import main as main_blueprint
    from app.api import api_bp
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_bp)

    # Prometheus Metrics
    REQUEST_COUNT = Counter('flask_request_count', 'App Request Count', ['method', 'endpoint', 'http_status'])
    REQUEST_LATENCY = Histogram('flask_request_latency_seconds', 'Request latency', ['endpoint'])

    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        request_latency = time.time() - getattr(request, 'start_time', time.time())
        REQUEST_LATENCY.labels(request.path).observe(request_latency)
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
        return response

    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handling middleware
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {error}')
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal Server Error'}, 500

    return app
