import base64
from datetime import datetime
from bson import ObjectId
from conections.mongo import conection_mongo
from conections.redis import conection_redis
import requests

def get_followers_list(token):
    """Fetch the list of followers from the /followers endpoint using the provided token."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://52.0.8.145:8080/followers", headers=headers, timeout=5)

        if response.status_code != 200:
            print(f"Failed to fetch followers: {response.status_code} - {response.text}")
            return []

        data = response.json()
        followers = data.get("followers", [])
        return [str(f["Id_User"]) for f in followers]

    except Exception as e:
        print(f"Exception occurred while fetching followers: {e}")
        return []

def create_publication(user_id, text, multimedia=None, token=None):
    db = conection_mongo()
    publications = db["Publications"]

    # Validate multimedia if present
    if multimedia:
        image_base64 = multimedia.get("image_base64")
        content_type = multimedia.get("content_type")
        if not image_base64 or not content_type:
            return {"error": "Multimedia must include image_base64 and content_type"}, 400
        try:
            base64.b64decode(image_base64)
        except Exception:
            return {"error": "Invalid base64 multimedia data"}, 400
    else:
        image_base64 = None
        content_type = None

    datepublish = datetime.utcnow()

    # Create the publication object
    publication = {
        "Id_user": user_id,
        "Text": text,
        "Multimedia": {
            "image_base64": image_base64,
            "content_type": content_type
        } if image_base64 else None,
        "Status": 1,
        "Datepublish": datepublish,
        "Likes": []
    }

    try:
        # Insert into MongoDB
        result = publications.insert_one(publication)
        publication_id = str(result.inserted_id)

        # Fetch followers
        followers = get_followers_list(token)

        # Send event to Redis stream with full content
        try:
            r = conection_redis()
            r.xadd("stream_user_publications", {
                "user_id": str(user_id),
                "publication_id": publication_id,
                "text": text,
                "image_base64": image_base64 or "",
                "content_type": content_type or "",
                "datepublish": datepublish.isoformat(),
                "followers": ",".join(followers)
            })
            print(f"Publication {publication_id} sent to Redis with content and followers.")
        except Exception as e:
            print(f"Failed to publish to Redis: {e}")

        return {
            "message": "Publication created",
            "publication_id": publication_id
        }, 201

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
