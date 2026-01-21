"""Enhanced Flask application for Retail Analytics Dashboard.

This is the main application file using the Flask factory pattern with
production-ready features including error handling, database integration,
and comprehensive logging.
"""

import os
import logging
from typing import Optional

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from config import get_config
from database import init_db, db, get_db_health
from errors import register_error_handlers, setup_logging, log_request_response
from models import Customer, Product, Category, Order, OrderItem


logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def create_app(config_name: Optional[str] = None) -> Flask:
    """Application factory for creating Flask app instances.
    
    Args:
        config_name: Configuration environment name (development, testing, production).
                    If None, uses FLASK_ENV environment variable.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app)
    logger.info(f"Starting {app.config['APP_NAME']} in {config_name or 'default'} mode")
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add request/response logging
    log_request_response(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register CLI commands
    _register_cli_commands(app)
    
    # Add application context processors
    _register_context_processors(app)
    
    logger.info("Application initialization complete")
    
    return app


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions.
    
    Args:
        app: Flask application instance.
    """
    # Initialize database
    init_db(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    logger.info(f"CORS enabled for origins: {app.config['CORS_ORIGINS']}")
    
    # Initialize JWT
    jwt = JWTManager(app)
    logger.info("JWT authentication initialized")
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'TokenExpired',
            'message': 'The token has expired',
            'status_code': 401
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'InvalidToken',
            'message': 'Signature verification failed',
            'status_code': 401
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'AuthorizationRequired',
            'message': 'Request does not contain an access token',
            'status_code': 401
        }), 401


def _register_blueprints(app: Flask) -> None:
    """Register Flask blueprints for modular routing.
    
    Args:
        app: Flask application instance.
    """
    # Import blueprints here to avoid circular imports
    # These will be created in subsequent files
    # from api.routes import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Register basic routes for now
    @app.route('/')
    def index():
        """Home page route."""
        return jsonify({
            'app': app.config['APP_NAME'],
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api': '/api/v1',
                'docs': '/api/docs'
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        db_health = get_db_health()
        
        overall_status = 'healthy' if db_health['status'] == 'healthy' else 'degraded'
        status_code = 200 if overall_status == 'healthy' else 503
        
        return jsonify({
            'status': overall_status,
            'timestamp': str(datetime.utcnow()),
            'services': {
                'database': db_health,
                'api': {'status': 'healthy'}
            }
        }), status_code
    
    logger.info("Blueprints registered")


def _register_cli_commands(app: Flask) -> None:
    """Register custom Flask CLI commands.
    
    Args:
        app: Flask application instance.
    """
    @app.cli.command('init-db')
    def init_database():
        """Initialize database tables."""
        from database import create_tables
        with app.app_context():
            create_tables()
            print("✓ Database tables created successfully")
    
    @app.cli.command('drop-db')
    def drop_database():
        """Drop all database tables."""
        from database import drop_tables
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == 'yes':
            with app.app_context():
                drop_tables()
                print("✓ Database tables dropped")
        else:
            print("Operation cancelled")
    
    @app.cli.command('seed-db')
    def seed_database():
        """Seed database with sample data."""
        with app.app_context():
            _seed_sample_data()
            print("✓ Database seeded with sample data")
    
    logger.info("CLI commands registered")


def _register_context_processors(app: Flask) -> None:
    """Register template context processors.
    
    Args:
        app: Flask application instance.
    """
    @app.context_processor
    def inject_config():
        """Inject configuration variables into templates."""
        return {
            'app_name': app.config['APP_NAME'],
            'debug': app.config['DEBUG']
        }


def _seed_sample_data() -> None:
    """Seed database with sample data for development/testing."""
    from database import db
    from datetime import datetime, timedelta
    import random
    
    # Create categories
    categories = [
        Category(name='Electronics', description='Electronic devices and accessories'),
        Category(name='Clothing', description='Apparel and fashion items'),
        Category(name='Home & Garden', description='Home improvement and garden supplies'),
        Category(name='Sports', description='Sports equipment and outdoor gear'),
        Category(name='Books', description='Books and educational materials'),
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.commit()
    logger.info(f"Created {len(categories)} categories")
    
    # Create products
    products = [
        Product(sku='ELEC-001', name='Wireless Headphones', category_id=1, price=79.99, cost=40.00, stock_quantity=50),
        Product(sku='ELEC-002', name='Smart Watch', category_id=1, price=199.99, cost=100.00, stock_quantity=30),
        Product(sku='CLOTH-001', name='Cotton T-Shirt', category_id=2, price=19.99, cost=8.00, stock_quantity=100),
        Product(sku='CLOTH-002', name='Jeans', category_id=2, price=49.99, cost=25.00, stock_quantity=75),
        Product(sku='HOME-001', name='Coffee Maker', category_id=3, price=89.99, cost=45.00, stock_quantity=40),
        Product(sku='SPORT-001', name='Yoga Mat', category_id=4, price=29.99, cost=15.00, stock_quantity=60),
        Product(sku='BOOK-001', name='Python Programming Guide', category_id=5, price=39.99, cost=20.00, stock_quantity=80),
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.commit()
    logger.info(f"Created {len(products)} products")
    
    # Create customers
    customers = [
        Customer(email='john.doe@example.com', first_name='John', last_name='Doe', 
                city='Miami', state='FL', country='USA', customer_segment='VIP'),
        Customer(email='jane.smith@example.com', first_name='Jane', last_name='Smith',
                city='Fort Lauderdale', state='FL', country='USA', customer_segment='Regular'),
        Customer(email='bob.jones@example.com', first_name='Bob', last_name='Jones',
                city='Pompano Beach', state='FL', country='USA', customer_segment='New'),
    ]
    
    for customer in customers:
        db.session.add(customer)
    
    db.session.commit()
    logger.info(f"Created {len(customers)} customers")
    
    # Create orders
    order_statuses = ['pending', 'processing', 'shipped', 'delivered']
    
    for i in range(10):
        customer = random.choice(customers)
        order_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        order = Order(
            order_number=f'ORD-{1000 + i}',
            customer_id=customer.id,
            order_date=order_date,
            status=random.choice(order_statuses),
            payment_method='credit_card'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Add 1-3 items to each order
        num_items = random.randint(1, 3)
        for _ in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                discount_amount=0.00
            )
            order_item.calculate_line_total()
            db.session.add(order_item)
        
        # Calculate order totals
        db.session.commit()
        order.calculate_totals()
        db.session.commit()
    
    logger.info("Created 10 sample orders with items")


# ==================== Application Entry Point ====================

if __name__ == '__main__':
    # Create application instance
    app = create_app()
    
    # Run development server
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
