import os
import logging
from flask import Flask

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Load configs
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Import and register routes
from routes.main_routes import main_bp
from routes.api_routes import api_bp

app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize storage
from utils.storage import init_storage
init_storage()

logging.info("Application initialized")
