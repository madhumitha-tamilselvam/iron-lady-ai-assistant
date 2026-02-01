function appendMessage(sender, text) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = sender;
    div.innerText = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const msg = input.value.trim();
    if (!msg) return;

    appendMessage("user", msg);
    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg})
    })
    .then(res => res.json())
    .then(data => {
        appendMessage("bot", data.reply);
        if (data.showMenu) {
            document.getElementById("menu").classList.remove("hidden");
        }
    });
}

function sendQuick(text) {
    appendMessage("user", text);
    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    })
    .then(res => res.json())
    .then(data => appendMessage("bot", data.reply));
}
