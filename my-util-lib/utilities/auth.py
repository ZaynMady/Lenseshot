import jwt
from functools import wraps
from flask import request, jsonify, g
from dotenv import load_dotenv
import os





#define get_current_user_id
def get_current_user_id(request, SUPABASE_JWT_SECRET):

    try:
        auth_header = request.headers.get("Authorization", None)

        #getting user ID
        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401

        token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
        user_id = decoded_token.get("sub")  # 'sub' = user_id in Supabase tokens
        return user_id, None, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({"message": "Invalid token"}), 401
#creating a wrapper function to ensure jwt token is required
def supabase_jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return "",200
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]

        try:
            # Decode and verify the token
            payload = jwt.decode(token,
                                 "94IWek04/8VSvcAG+x619owuOAUSx3MFaqAVUme5DwhMSLaLb0rj7pt/vKJtX78yMUmFdai5mzx76y+8zV51kQ==", 
                                 algorithms=["HS256"], 
                                 options={"verify_aud" : False})
            # store user info globally (similar to get_jwt_identity)
            g.current_user = payload["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"message": f"Invalid token: {str(e)}"}), 401

        return f(*args, **kwargs)
    return decorated