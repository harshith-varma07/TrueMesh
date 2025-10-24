#!/usr/bin/env python
"""
Database initialization and seeding script for TrueMesh Provider Intelligence
"""
import os
import sys
from pathlib import Path
import asyncio
from datetime import datetime

from app.core.database import engine, Base
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.models import *

setup_logging()
logger = get_logger("init_db")


def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        return False


def seed_sample_data():
    """Seed database with sample data"""
    try:
        from sqlalchemy.orm import Session
        
        logger.info("Seeding sample data...")
        
        with Session(engine) as session:
            # Check if data already exists
            from app.models import Provider
            existing_count = session.query(Provider).count()
            
            if existing_count > 0:
                logger.info(f"Database already has {existing_count} providers, skipping seed")
                return True
            
            # Create sample providers
            import uuid
            sample_providers = [
                Provider(
                    id=uuid.uuid4(),
                    registration_number="MCI123456",
                    name="Dr. Amit Sharma",
                    provider_type="doctor",
                    specialization="Cardiology",
                    email="amit.sharma@example.com",
                    phone="+919876543210",
                    city="Mumbai",
                    state="Maharashtra",
                    country="India",
                    status="pending",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                Provider(
                    id=uuid.uuid4(),
                    registration_number="HOSP789012",
                    name="Apollo Hospital - Delhi",
                    provider_type="hospital",
                    specialization="Multi-Specialty",
                    email="info@apollodelhi.com",
                    phone="+911123456789",
                    address_line1="Sarita Vihar",
                    city="Delhi",
                    state="Delhi",
                    country="India",
                    status="pending",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                Provider(
                    id=uuid.uuid4(),
                    registration_number="PHARM345678",
                    name="MedPlus Pharmacy - Bangalore",
                    provider_type="pharmacy",
                    email="bangalore@medplus.com",
                    phone="+918012345678",
                    address_line1="Koramangala",
                    city="Bangalore",
                    state="Karnataka",
                    country="India",
                    status="pending",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            ]
            
            for provider in sample_providers:
                session.add(provider)
            
            session.commit()
            
            logger.info(f"✓ Seeded {len(sample_providers)} sample providers")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to seed data: {str(e)}")
        return False


def main():
    """Main initialization function"""
    settings = get_settings()
    
    logger.info("Starting database initialization...")
    logger.info(f"Database URL: {settings.database_url}")
    
    # Create tables
    if not create_tables():
        logger.error("Failed to create tables")
        return False
    
    # Seed sample data
    if not seed_sample_data():
        logger.error("Failed to seed data")
        return False
    
    logger.info("✓ Database initialization completed successfully")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
