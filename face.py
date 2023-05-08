from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

import cv2
import numpy as np
from PIL import Image

class FaceDetectionResult(BaseModel):
    user_id: int
    image_b64: str
    created_at: datetime

    class Config:
        orm_mode = False

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

def store_face_results(db: sessionmaker, user_id: int, face_result: dict):
    result = FaceDetectionResult(user_id=user_id, detection_result=face_result, created_at=datetime.now())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result
