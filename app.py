from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

USER_API = "https://users.roblox.com/v1/usernames/users"
THUMB_API = "https://thumbnails.roblox.com/v1/users/avatar-headshot"

def username_to_userid(username):
    payload = {
        "usernames": [username],
        "excludeBannedUsers": False
    }

    r = requests.post(USER_API, json=payload, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json()
    if not data.get("data"):
        return None

    return data["data"][0]["id"]

# GET /api/roblox/avatar-headshot?username=SomeUser
@app.route("/api/roblox/avatar-headshot", methods=["GET"])
def avatar_by_username():
    username = request.args.get("username", "").strip()
    size = request.args.get("size", "100x100")
    format_ = request.args.get("format", "Png")
    is_circular = request.args.get("isCircular", "true")

    if not username:
        return jsonify({"error": "username is required"}), 400

    user_id = username_to_userid(username)
    if not user_id:
        return jsonify({"error": "username not found"}), 404

    # Call REAL Roblox thumbnail API
    thumb_response = requests.get(
        THUMB_API,
        params={
            "userIds": user_id,
            "size": size,
            "format": format_,
            "isCircular": is_circular
        },
        timeout=10
    )

    # Return Roblox response AS-IS
    return jsonify(thumb_response.json()), thumb_response.status_code


if __name__ == "__main__":
    app.run(debug=True)
