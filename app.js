const chatBox = document.getElementById("chat-box");
const input = document.getElementById("input");

// Enter fix
input.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = "msg " + sender;
    msg.innerHTML = `<div class="bubble">${text}</div>`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    addMessage("...", "bot");

    const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ message: text })
    });

    const data = await res.json();

    chatBox.lastChild.remove();
    addMessage(data.reply, "bot");
}

// Login
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (data.msg === "logged in") {
        document.getElementById("loginBox").style.display = "none";
        loadHistory();
    } else {
        alert("Invalid login");
    }
}

// Register
async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({ username, password })
    });

    alert("Registered!");
}

// Guest mode
function skipLogin() {
    document.getElementById("loginBox").style.display = "none";
}

// Load history
async function loadHistory() {
    const res = await fetch("http://127.0.0.1:5000/history", {
        credentials: "include"
    });

    const data = await res.json();

    data.forEach(chat => {
        addMessage(chat.msg, "user");
        addMessage(chat.reply, "bot");
    });
}

function newChat() {
    chatBox.innerHTML = "";
}