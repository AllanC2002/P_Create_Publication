from flask import Flask, request, jsonify
import jwt
import os
from dotenv import load_dotenv
from services.functions import create_publication

load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")

@app.route("/create-publication", methods=["POST"])
def create_publication_route():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token missing or invalid"}), 401

    token = auth_header.replace("Bearer ", "")

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token data"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    data = request.get_json()
    if not data or "Text" not in data:
        return jsonify({"error": "Text field is required"}), 400

    text = data["Text"]
    multimedia = data.get("Multimedia")  # it has optional multimedia data

    # Pass the user_id, text, multimedia, and token to the service function
    response, code = create_publication(user_id, text, multimedia, token)
    return jsonify(response), code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
