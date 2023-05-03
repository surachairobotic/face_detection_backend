from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create the engine
engine = create_engine("postgresql://facedb:1234@localhost/database")

# Define the Base class
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    api_quota_limit = Column(Integer, default=100)

# Create the table
Base.metadata.create_all(bind=engine)
