import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24

def create_access_token(user_id: int):
    # Define the token expiration time
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + expires_delta
    
    # Define the token payload
    token_payload = {'user_id': user_id, 'exp': expires_at}
    
    # Generate and return the JWT access token
    access_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    return access_token

def create_refresh_token(user_id: int):
    # Define the token expiration time
    expires_delta = timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    expires_at = datetime.utcnow() + expires_delta
    
    # Define the token payload
    token_payload = {'user_id': user_id, 'exp': expires_at}
    
    # Generate and return the JWT refresh token
    refresh_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token

def decode_token(token: str, is_refresh_token: bool = False) -> int:
    try:
        # Decode the JWT token using the secret key
        if is_refresh_token:
            #payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM + '-REFRESH'])
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the user information from the payload
        user_id = payload['user_id']
        print('user_id: ', user_id)
        print('exp: ', payload['exp'])
                
        # Return the user object
        return user_id
    except jwt.DecodeError:
        # Handle decoding errors as needed
        print("DecodeError")
        return -1
    except jwt.ExpiredSignatureError:
        # Handle expired tokens as needed
        print("ExpiredSignatureError")
        return -2