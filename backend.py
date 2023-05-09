from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List
import base64

from jwt_utils import create_access_token, create_refresh_token, decode_token

import io
from PIL import Image
import base64

from PIL import Image

from face import *

import cv2
from moviepy.editor import VideoFileClip

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

class FaceDetectionResult(Base):
    __tablename__ = 'face_detection_results'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    image_b64 = Column(String)
    created_at = Column(DateTime)

def base64_safe(image_data):
    #print(image_data)
    return image_data.replace('+', '-*-').replace('/', '_|_')

def base64_safe_decode(image_data):
    #print(image_data)
    return image_data.replace('-*-', '+').replace('_|_', '/')

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

class Image64(BaseModel):
    image_b64: str
class Image64Token(BaseModel):
    image_b64: str
    access_token: str

class QueryDateTime(BaseModel):
    access_token: str
    dt_from: str
    dt_to: str

# class FaceDetectionResult(BaseModel):
#     user_id: int
#     image_b64: str
#     created_at: datetime

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
            return HTTPException(status_code=200, detail={'access_token': access_token, 'refresh_token': refresh_token, 'api_quota_limit': db_user.api_quota_limit})
        
        else:
            # Return an error response if the email or password is invalid
            return HTTPException(status_code=401, detail="Incorrect email or password")
    
    finally:
        # Close the session
        session.close()

def store_face_results(db: sessionmaker, user_id: int, face_result: str):
    #print(face_result)
    #print(type(face_result))
    b64_safe = base64_safe(face_result)
    result = FaceDetectionResult(user_id=user_id, image_b64=b64_safe, created_at=datetime.now())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

@app.post('/process_image', response_model=Image64)
def process_image(image: Image64Token):
    print('//process_image')
    # Open a new database session
    session = Session()
    
    try:
        # Check that the user is authenticated and has enough API quota remaining
        user_id = decode_token(image.access_token)
        if user_id == -1:
            raise HTTPException(status_code=401, detail="DecodeError")
        elif user_id == -2:
            raise HTTPException(status_code=402, detail="ExpiredSignatureError")

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
        
        # print('START')
        # print(processed_image_b64)
        # x = base64_safe(processed_image_b64)
        # print('START22222222')
        # print(x)
        # y = base64_safe_decode(x)
        # print('START33333333')
        # print(y)

        store_face_results(session, user_id, processed_image_b64)

        # Return the result in the response
        return result
    
    finally:
        # Close the session
        session.close()

@app.post("/query_images", response_model=List[str])
def query_images(msg: QueryDateTime):
    print(msg)
    # Open a new database session
    session = Session()

    # verify access token and get user id
    user_id = decode_token(msg.access_token)
    if user_id == -1:
        raise HTTPException(status_code=401, detail="DecodeError")
    elif user_id == -2:
        raise HTTPException(status_code=402, detail="ExpiredSignatureError")

    # convert ISO 8601 strings to datetime objects
    try:
        dt_from = datetime.fromisoformat(msg.dt_from)
        dt_to = datetime.fromisoformat(msg.dt_to)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    print('user_id=', user_id)
    # query database for image_b64s
    # results = session.query(FaceDetectionResult).filter(FaceDetectionResult.user_id == user_id,
    #                                               FaceDetectionResult.created_at >= dt_from, 
    #                                               FaceDetectionResult.created_at <= dt_to).all()
    results = session.query(FaceDetectionResult).filter(FaceDetectionResult.user_id == user_id)
    # results = session.query(FaceDetectionResult).order_by(FaceDetectionResult.created_at.desc()).first()

    # image_b64 = base64_safe_decode(results.image_b64)
    # print(image_b64)
    image_b64s = [base64_safe_decode(result.image_b64) for result in results]
    #print(image_b64s)

    return image_b64s

@app.post("/process_video")
async def process_video(video: UploadFile = File(...)):
    # Save the uploaded video file to disk
    file_path = "uploaded_video.mp4"
    with open(file_path, "wb") as f:
        f.write(await video.read())

    # Perform face detection and annotate the video
    processed_path = detect_faces2(file_path)

    # Return the processed video file
    return StreamingResponse(open(processed_path, "rb"), media_type="video/mp4")

def detect_faces2(file_path):
    # Load the video using MoviePy
    clip = VideoFileClip(file_path)

    # Initialize the face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Define a function to apply face detection on each frame of the video
    def detect(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return frame

    # Apply the face detection function to each frame of the video
    processed_clip = clip.fl_image(detect)

    # Save the processed video to disk
    processed_path = "processed_video.mp4"
    processed_clip.write_videofile(processed_path, codec="libx264", audio_codec="aac")

    return processed_path