from flask import Blueprint
from .classification import bp as classification_bp
from .inventory      import bp as inventory_bp
from .barcode        import bp as barcode_bp

def register_blueprints(app):
    app.register_blueprint(classification_bp, url_prefix='/api')
    app.register_blueprint(inventory_bp,url_prefix='/api')
    app.register_blueprint(barcode_bp,url_prefix='/api')