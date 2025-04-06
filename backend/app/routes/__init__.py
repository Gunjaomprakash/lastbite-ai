from flask import Blueprint
from .classification import bp as classification_bp

def register_blueprints(app):
    app.register_blueprint(classification_bp, url_prefix='/api')