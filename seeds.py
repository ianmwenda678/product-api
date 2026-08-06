from database.session import get_session, create_tables
from models.user import User
from models.product import Product
from auth import hash_password
from datetime import datetime, timedelta
import random
from sqlmodel import select

def seed_data():
    create_tables()
    
    with next(get_session()) as session:
        # Check if users already exist
        existing = session.exec(select(User)).first()
        if existing:
            print("Database already seeded. Skipping...")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@productapi.com",
            hashed_password=hash_password("admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        session.add(admin)
        
        # Create regular users
        users = []
        for i in range(1, 4):
            user = User(
                username=f"user{i}",
                email=f"user{i}@productapi.com",
                hashed_password=hash_password(f"user{i}123"),
                full_name=f"User {i}",
                role="user",
                is_active=True
            )
            session.add(user)
            users.append(user)
        
        session.commit()
        
        # Create sample products
        product_names = ["Laptop", "Phone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse"]
        
        for i in range(20):
            product = Product(
                name=random.choice(product_names) + f" {i+1}",
                description=f"Sample product {i+1}",
                price=round(random.uniform(10.99, 999.99), 2),
                stock=random.randint(0, 100),
                owner_id=random.choice([admin.id] + [u.id for u in users]),
                created_at=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            session.add(product)
        
        session.commit()
        print("Database seeded successfully!")
        print(f"Created 1 admin, 3 users, and 20 products")

if __name__ == "__main__":
    seed_data()
