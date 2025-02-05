var socket = io.connect('http://' + document.domain + ':' + location.port);
var username = "";
var publicVapidKey = "{{ vapid_public_key }}";

function login() {
    username = document.getElementById("username").value;
    if (username) {
        socket.emit('login', { username: username });
        socket.emit('request_online_users');
        subscribeToPushNotifications();
    }
}

function logout() {
    if (username) {
        socket.emit('logout', { username: username });
        username = "";
        document.getElementById("online-users").innerHTML = "";
    }
}

function sendMessage() {
    var recipient = document.getElementById("recipient").value;
    var message = document.getElementById("message").value;
    
    if (username && recipient && message) {
        console.log(`Sending message: ${message} to ${recipient}`);
        socket.emit('private_message', { sender: username, recipient: recipient, message: message });
    }
}

// แสดงข้อความที่ได้รับ
socket.on('receive_message', function(data) {
    var chatBox = document.getElementById("chat-box");
    var newMessage = document.createElement("p");
    newMessage.textContent = data.sender + ": " + data.message;
    chatBox.appendChild(newMessage);
});

// อัปเดตรายชื่อผู้ใช้ออนไลน์
socket.on('user_status', function(data) {
    var userList = document.getElementById("online-users");
    if (data.status === "online") {
        var li = document.createElement("li");
        li.textContent = data.username;
        li.setAttribute("id", "user-" + data.username);
        userList.appendChild(li);
    } else {
        var userElement = document.getElementById("user-" + data.username);
        if (userElement) {
            userElement.remove();
        }
    }
});

// สมัครรับ Push Notifications
async function subscribeToPushNotifications() {
    if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register('/static/sw.js');
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: publicVapidKey
        });

        fetch('/subscribe', {
            method: 'POST',
            body: JSON.stringify({ username: username, subscription: subscription }),
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
