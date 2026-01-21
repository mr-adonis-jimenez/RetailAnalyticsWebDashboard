"""Database connection and session management for Retail Analytics Dashboard.

This module provides SQLAlchemy database setup, connection pooling,
and session management with error handling.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import Pool

from errors import DatabaseError


logger = logging.getLogger(__name__)

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask) -> None:
    """Initialize database with Flask application.
    
    Args:
        app: Flask application instance.
        
    Raises:
        DatabaseError: If database initialization fails.
    """
    try:
        # Initialize SQLAlchemy
        db.init_app(app)
        
        # Initialize Flask-Migrate for database migrations
        migrate.init_app(app, db)
        
        # Register database event listeners
        _register_event_listeners()
        
        # Test database connection
        with app.app_context():
            test_connection()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.critical(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise DatabaseError(f"Database initialization failed: {str(e)}")


def test_connection() -> bool:
    """Test database connection.
    
    Returns:
        bool: True if connection is successful.
        
    Raises:
        DatabaseError: If connection test fails.
    """
    try:
        # Execute a simple query to test connection
        db.session.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}", exc_info=True)
        raise DatabaseError(f"Cannot connect to database: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise DatabaseError(f"Database error: {str(e)}")


def create_tables() -> None:
    """Create all database tables.
    
    This should be called within an application context.
    
    Raises:
        DatabaseError: If table creation fails.
    """
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create tables: {str(e)}", exc_info=True)
        raise DatabaseError(f"Table creation failed: {str(e)}")


def drop_tables() -> None:
    """Drop all database tables.
    
    WARNING: This will delete all data. Use with caution!
    
    Raises:
        DatabaseError: If table dropping fails.
    """
    try:
        db.drop_all()
        logger.warning("All database tables dropped")
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop tables: {str(e)}", exc_info=True)
        raise DatabaseError(f"Table dropping failed: {str(e)}")


@contextmanager
def session_scope() -> Generator:
    """Provide a transactional scope for database operations.
    
    Usage:
        with session_scope() as session:
            session.add(new_object)
            # Changes are automatically committed
    
    Yields:
        Session: SQLAlchemy database session.
        
    Raises:
        DatabaseError: If database operation fails.
    """
    session = db.session
    try:
        yield session
        session.commit()
        logger.debug("Database transaction committed")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database transaction failed, rolling back: {str(e)}", exc_info=True)
        raise DatabaseError(f"Database operation failed: {str(e)}")
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in transaction: {str(e)}", exc_info=True)
        raise


def safe_commit() -> bool:
    """Safely commit current database session.
    
    Returns:
        bool: True if commit successful, False otherwise.
    """
    try:
        db.session.commit()
        logger.debug("Database session committed")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Commit failed, rolling back: {str(e)}", exc_info=True)
        return False


def safe_rollback() -> None:
    """Safely rollback current database session."""
    try:
        db.session.rollback()
        logger.debug("Database session rolled back")
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}", exc_info=True)


# ==================== Event Listeners ====================

def _register_event_listeners() -> None:
    """Register SQLAlchemy event listeners for monitoring and optimization."""
    
    @event.listens_for(Engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Called when a new database connection is created."""
        logger.debug("New database connection established")
    
    @event.listens_for(Engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Called when a connection is retrieved from the pool."""
        logger.debug("Database connection checked out from pool")
    
    @event.listens_for(Engine, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        """Called when a connection is returned to the pool."""
        logger.debug("Database connection returned to pool")
    
    @event.listens_for(Pool, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Set SQLite-specific optimizations (if using SQLite)."""
        if 'sqlite' in str(type(dbapi_conn)):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
            logger.debug("SQLite pragmas set")


# ==================== Health Check ====================

def get_db_health() -> dict:
    """Get database health status.
    
    Returns:
        dict: Database health information.
    """
    try:
        # Test connection
        db.session.execute(text("SELECT 1"))
        
        # Get pool status
        pool = db.engine.pool
        
        return {
            "status": "healthy",
            "connected": True,
            "pool_size": pool.size(),
            "checked_out_connections": pool.checkedout(),
            "overflow_connections": pool.overflow(),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }


# ==================== Utility Functions ====================

def execute_raw_sql(sql: str, params: Optional[dict] = None) -> list:
    """Execute raw SQL query safely.
    
    Args:
        sql: SQL query string.
        params: Query parameters (optional).
        
    Returns:
        list: Query results.
        
    Raises:
        DatabaseError: If query execution fails.
    """
    try:
        result = db.session.execute(text(sql), params or {})
        return result.fetchall()
    except SQLAlchemyError as e:
        logger.error(f"Raw SQL execution failed: {str(e)}", exc_info=True)
        raise DatabaseError(f"Query execution failed: {str(e)}")


def paginate_query(query, page: int = 1, per_page: int = 20) -> dict:
    """Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object.
        page: Page number (1-indexed).
        per_page: Items per page.
        
    Returns:
        dict: Paginated results with metadata.
    """
    try:
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            "items": [item.to_dict() for item in paginated.items],
            "total": paginated.total,
            "pages": paginated.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
        }
    except Exception as e:
        logger.error(f"Pagination failed: {str(e)}", exc_info=True)
        raise DatabaseError(f"Pagination failed: {str(e)}")
