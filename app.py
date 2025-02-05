from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from pywebpush import webpush, WebPushException
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

active_users = {}  # เก็บ session id ของผู้ใช้ออนไลน์
user_subscriptions = {}  # เก็บ Web Push Subscription ของแต่ละ user

VAPID_PUBLIC_KEY = "YOUR_VAPID_PUBLIC_KEY"
VAPID_PRIVATE_KEY = "YOUR_VAPID_PRIVATE_KEY"

@app.route('/')
def index():
    return render_template('index.html', vapid_public_key=VAPID_PUBLIC_KEY)

@socketio.on('login')
def handle_login(data):
    username = data['username']
    active_users[username] = request.sid
    emit('user_status', {'username': username, 'status': 'online'}, broadcast=True)
    print(f"{username} logged in.")

@socketio.on('logout')
def handle_logout(data):
    username = data['username']
    if username in active_users:
        del active_users[username]
        emit('user_status', {'username': username, 'status': 'offline'}, broadcast=True)
        print(f"{username} logged out.")

@socketio.on('private_message')
def handle_private_message(data):
    sender = data['sender']
    recipient = data['recipient']
    message = data['message']
    
    print(f"📩 Message from {sender} to {recipient}: {message}")  # Debug
    print(f"🔎 Active Users: {active_users}")  # ดูว่า room ของผู้รับมีอยู่ไหม
    
    if recipient in active_users:
        recipient_sid = active_users[recipient]  # หา session ID ของผู้รับ
        print(f"📡 Sending message to room: {recipient_sid}")  # Debug
        emit('receive_message', {'sender': sender, 'message': message}, room=recipient_sid)
    else:
        emit('update', f"{recipient} is not online.", room=active_users.get(sender, ''))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    username = data['username']
    subscription = data['subscription']

    if username:
        user_subscriptions[username] = subscription
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

def send_push_notification(subscription, message):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps({"title": "Chat Notification", "message": message}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": "mailto:your-email@example.com"}
        )
    except WebPushException as ex:
        print(f"Error sending push notification: {ex}")

if __name__ == '__main__':
    socketio.run(app, debug=True)
