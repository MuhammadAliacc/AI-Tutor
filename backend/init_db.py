#!/usr/bin/env python
"""
Initialize database with demo data
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, engine, SessionLocal
from app.models.database import User, UserRole
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Create demo users
db = SessionLocal()

# Check if users already exist
admin = db.query(User).filter(User.email == "admin@example.com").first()
if not admin:
    admin = User(
        email="admin@example.com",
        name="Admin User",
        hashed_password=get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    print("✓ Created admin user: admin@example.com / adminpass123")

student = db.query(User).filter(User.email == "student@example.com").first()
if not student:
    student = User(
        email="student@example.com",
        name="Demo Student",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(student)
    print("✓ Created student user: student@example.com / password123")

db.commit()
db.close()

print("\n✓ Database initialization complete!")
print("✓ Tables created")
print("✓ Demo users added")
