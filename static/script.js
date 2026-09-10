

async function createNewChat() {

    try {

        const response = await fetch(
            "/api/new-chat",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );

        const data = await response.json();

        if (data.error) {

            alert(
                data.error
            );

            return;
        }

        currentConversationId =
            data.conversation_id;

        const chatBox =
            document.getElementById(
                "chat-box"
            );

        chatBox.innerHTML = `

            <div class="welcome-screen">

                <div class="welcome-icon">
                    ✦
                </div>

                <h2>
                    How can I help you today?
                </h2>

                <p>
                    Ask anything. NAD AI is ready to help.
                </p>

            </div>

        `;

        const historyContainer =
            document.getElementById(
                "chat-history"
            );

        const newChatButton =
            document.createElement(
                "button"
            );

        newChatButton.className =
            "history-chat";

        newChatButton.onclick =
            function () {

                loadChat(
                    currentConversationId
                );

            };

        newChatButton.innerHTML = `

            💬

            <span>
                ${data.title}
            </span>

        `;

        historyContainer.prepend(
            newChatButton
        );

        document.getElementById(
            "user-input"
        ).focus();

    } catch (error) {

        console.error(
            "NEW CHAT ERROR:",
            error
        );

    }

}


/* =========================================
LOAD OLD CHAT
========================================= */

async function loadChat(
    conversationId
) {

    try {

        const response =
            await fetch(
                `/api/chat/${conversationId}`
            );

        const data =
            await response.json();

        if (data.error) {

            alert(
                data.error
            );

            return;
        }

        currentConversationId =
            conversationId;

        const chatBox =
            document.getElementById(
                "chat-box"
            );

        chatBox.innerHTML =
            "";

        data.messages.forEach(
            function (message) {

                addMessage(
                    message.content,
                    message.role === "user"
                        ? "user"
                        : "bot"
                );

            }
        );

        chatBox.scrollTop =
            chatBox.scrollHeight;

    } catch (error) {

        console.error(
            "LOAD CHAT ERROR:",
            error
        );

    }

}


/* =========================================
ADD MESSAGE TO SCREEN
========================================= */

function addMessage(
    text,
    sender
) {

    const chatBox =
        document.getElementById(
            "chat-box"
        );

    const welcomeScreen =
        chatBox.querySelector(
            ".welcome-screen"
        );

    if (welcomeScreen) {

        welcomeScreen.remove();

    }

    const messageDiv =
        document.createElement(
            "div"
        );

    messageDiv.classList.add(
        "message"
    );

    if (sender === "user") {

        messageDiv.classList.add(
            "user-message"
        );

    } else {

        messageDiv.classList.add(
            "bot-message"
        );

    }

    messageDiv.textContent =
        text;

    chatBox.appendChild(
        messageDiv
    );

    chatBox.scrollTop =
        chatBox.scrollHeight;

}


/* =========================================
SEND MESSAGE
========================================= */

async function sendMessage(
    event
) {

    event.preventDefault();

    const input =
        document.getElementById(
            "user-input"
        );

    const message =
        input.value.trim();

    if (!message) {

        return;

    }

    addMessage(
        message,
        "user"
    );

    input.value =
        "";

    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            message: message,

                            conversation_id:
                                currentConversationId
                        }
                    )
                }
            );

        const data =
            await response.json();

        if (data.error) {

            addMessage(
                data.error,
                "bot"
            );

            return;

        }

        if (
            data.conversation_id
        ) {

            currentConversationId =
                data.conversation_id;

        }

        addMessage(
            data.reply,
            "bot"
        );

    } catch (error) {

        console.error(
            "CHAT ERROR:",
            error
        );

        addMessage(
            "Sorry, something went wrong. Please try again.",
            "bot"
        );

    }

}


/* =========================================
ATTACHMENT MESSAGE
========================================= */

function showAttachmentMessage() {

    alert(
        "Image and PDF upload features will be added soon!"
    );

}


/* =========================================
AUTO RESIZE TEXTAREA
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const input =
            document.getElementById(
                "user-input"
            );

        if (input) {

            input.addEventListener(
                "input",
                function () {

                    this.style.height =
                        "auto";

                    this.style.height =
                        Math.min(
                            this.scrollHeight,
                            150
                        )
                        + "px";

                }
            );

        }

    }
);
const voiceButton = document.getElementById("voice-button");
const userInput = document.getElementById("user-input");

function setMicIcon() {

voiceButton.innerHTML = `
    <svg
        class="voice-icon"
        viewBox="0 0 24 24"
        aria-hidden="true"
    >
        <path d="M12 15a3 3 0 0 0 3-3V7a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3Z"/>
        <path d="M5 11a7 7 0 0 0 14 0"/>
        <path d="M12 18v3"/>
        <path d="M8 21h8"/>
    </svg>
`;

}

setMicIcon();

if ("webkitSpeechRecognition" in window) {

const recognition = new webkitSpeechRecognition();

recognition.continuous = false;

recognition.interimResults = false;

recognition.lang = "en-US";


voiceButton.addEventListener(
    "click",
    function () {

        recognition.start();

        voiceButton.innerHTML = "🔴";

    }
);


recognition.onresult = function (event) {

    const voiceText =
        event.results[0][0].transcript;

    userInput.value =
        voiceText;

    setMicIcon();

    

};


recognition.onerror = function () {

    setMicIcon();

};


recognition.onend = function () {

    setMicIcon();

};

}

else {

voiceButton.addEventListener(
    "click",
    function () {

        alert(
            "Voice recognition is not supported in this browser."
        );

    }
);

}