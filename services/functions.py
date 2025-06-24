import base64
from datetime import datetime
from bson import ObjectId
from conections.mongo import conection_mongo
from conections.redis import conection_redis

def create_publication(user_id, text, multimedia=None):
    db = conection_mongo()
    publications = db["Publications"]

    if multimedia:
        image_base64 = multimedia.get("image_base64")
        content_type = multimedia.get("content_type")
        if not image_base64 or not content_type:
            return {"error": "Multimedia must have image_base64 and content_type"}, 400
        try:
            base64.b64decode(image_base64)
        except Exception:
            return {"error": "Invalid base64 multimedia data"}, 400
    else:
        image_base64 = None
        content_type = None

    publication = {
        "Id_user": user_id,
        "Text": text,
        "Multimedia": {
            "image_base64": image_base64,
            "content_type": content_type
        } if image_base64 else None,
        "Status": 1,
        "Datepublish": datetime.utcnow(),
        "Likes": []
    }

    try:
        result = publications.insert_one(publication)
        publication_id = str(result.inserted_id)

        # Event
        try:
            r = conection_redis()
            r.xadd("stream_user_publications", {
                "user_id": str(user_id),
                "publication_id": publication_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            print("Success to publish to redis")
        except Exception as e:
            print("Error to publish to redis:", e)

        return {
            "message": "Publication created",
            "publication_id": publication_id
        }, 201

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
