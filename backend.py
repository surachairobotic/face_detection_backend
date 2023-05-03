from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

# Define the database connection string
DB_CONN_STRING = "postgresql://facedb:1234@localhost:5432/database"

# Define the SQLAlchemy engine and session maker
engine = create_engine(DB_CONN_STRING)
Session = sessionmaker(bind=engine)

# Define the SQLAlchemy Base object
Base = declarative_base()

# Define the User SQLAlchemy model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    api_quota_limit = Column(Integer, default=100)

    def to_dict(self):
        return {"id": self.id, "user_name": self.user_name, "email": self.email, "api_quota_limit": self.api_quota_limit}

# Create the database tables (if they don't already exist)
Base.metadata.create_all(bind=engine)

# Define the Pydantic model for user registration
class UserRegistration(BaseModel):
    user_name: str
    email: str
    password: str
    api_quota_limit: int = 100

@app.get('/')
def root():
    return {'message': 'Hello World'}

@app.post("/register")
async def register(user: UserRegistration):
    if user.user_name == '' or user.email == '' or user.password == '':
        raise HTTPException(status_code=400, detail="Invalid username or email.")

    # Add the new User to the database
    session = Session()

    existing_user = session.query(User).filter(User.user_name == user.user_name).first()
    existing_email = session.query(User).filter(User.email == user.email).first()
    if existing_user or existing_email:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    # Create a new User object using the Pydantic model data
    new_user = User(user_name=user.user_name, email=user.email, password=user.password, api_quota_limit=user.api_quota_limit)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Return the newly created User object as a dictionary
    return new_user.to_dict()

