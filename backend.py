from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from jwt_utils import create_access_token, create_refresh_token, decode_token

import io
from PIL import Image
import base64

import cv2
import numpy as np
from PIL import Image

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

class UserLogin(BaseModel):
    email: str
    password: str

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
    session.close()

    # Return the newly created User object as a dictionary
    return new_user.to_dict()

@app.post('/login')
def login_user(user: UserLogin):
    # Open a new database session
    session = Session()
    
    try:
        # Query the database for the user with the given email address
        db_user = session.query(User).filter_by(email=user.email).first()
        
        # Verify that the password matches the stored hash
        if db_user and db_user.password == user.password:
            # Create access and refresh tokens for the user
            access_token = create_access_token(db_user.id)
            decode_token(access_token)
            refresh_token = create_refresh_token(db_user.id)
            decode_token(refresh_token)
            
            # Return the tokens in the response
            return HTTPException(status_code=200, detail={'access_token': access_token, 'refresh_token': refresh_token})
        
        else:
            # Return an error response if the email or password is invalid
            return HTTPException(status_code=401, detail="Incorrect email or password")
    
    finally:
        # Close the session
        session.close()

class Image64(BaseModel):
    image_b64: str
class Image64Token(BaseModel):
    image_b64: str
    access_token: str

@app.post('/process_image', response_model=Image64)
def process_image(image: Image64Token):
    #print('image : ', image)
    # Open a new database session
    session = Session()
    
    try:
        # Check that the user is authenticated and has enough API quota remaining
        user_id = decode_token(image.access_token)
        if user_id == -1:
            return HTTPException(status_code=401, detail="DecodeError")
        elif user_id == -2:
            return HTTPException(status_code=402, detail="ExpiredSignatureError")

        # Decode the base64 image data into binary data
        image_data = base64.b64decode(image.image_b64)
        
        # Read the image data into memory
        image_bytes = io.BytesIO(image_data)
        
        # Open the image using the PIL library
        pil_image = Image.open(image_bytes)
        
        # Perform some processing on the image (e.g., resizing, cropping, filtering)
        pil_image = detect_faces(pil_image)
        
        # Convert the processed image back to bytes and encode it as base64
        processed_image_bytes = io.BytesIO()
        pil_image.save(processed_image_bytes, format='JPEG')
        processed_image_b64 = base64.b64encode(processed_image_bytes.getvalue()).decode('utf-8')
        
        # Create a new ImageProcessingResult object containing the processed image in base64 format
        result = Image64(image_b64=processed_image_b64)
        
        # Return the result in the response
        return result
    
    finally:
        # Close the session
        session.close()

def detect_faces(image):
    # Convert PIL image to NumPy array
    np_image = np.array(image)
    
    # Convert image to grayscale
    gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
    
    # Load pre-trained Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    # Draw rectangles around the detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(np_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Convert the modified NumPy array back to a PIL image and return it
    return Image.fromarray(np_image)