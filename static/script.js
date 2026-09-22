
let currentConversationId = null;


/* =========================================
CREATE NEW CHAT
========================================= */

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

            alert(data.error);
            return;

        }

        currentConversationId =
            data.conversation_id;

        const chatBox =
            document.getElementById("chat-box");

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

            alert(data.error);
            return;

        }

        currentConversationId =
            conversationId;

        const chatBox =
            document.getElementById(
                "chat-box"
            );

        chatBox.innerHTML = "";

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
ADD MESSAGE
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

    input.value = "";

    /* Thinking message */

    const thinkingId =
        "thinking-" + Date.now();

    const chatBox =
        document.getElementById(
            "chat-box"
        );

    const thinkingDiv =
        document.createElement(
            "div"
        );

    thinkingDiv.id =
        thinkingId;

    thinkingDiv.className =
        "message bot-message";

    thinkingDiv.textContent =
        "NAD AI is thinking...";

    chatBox.appendChild(
        thinkingDiv
    );

    chatBox.scrollTop =
        chatBox.scrollHeight;


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


        /* Remove thinking message */

        const thinkingMessage =
            document.getElementById(
                thinkingId
            );

        if (thinkingMessage) {

            thinkingMessage.remove();

        }


        /* Error */

        if (!response.ok) {

            addMessage(
                data.error ||
                data.reply ||
                "NAD AI is not responding right now.",
                "bot"
            );

            return;

        }


        if (data.error) {

            addMessage(
                data.error,
                "bot"
            );

            return;

        }


        /* Save conversation ID */

        if (data.conversation_id) {

            currentConversationId =
                data.conversation_id;

        }


        /* Image response */

        if (data.image) {

            addMessage(
                data.reply ||
                "Here is your generated image! 🖼️",
                "bot"
            );

            const imageDiv =
                document.createElement(
                    "div"
                );

            imageDiv.className =
                "message bot-message";

            const image =
                document.createElement(
                    "img"
                );

            image.src =
                data.image;

            image.alt =
                "Generated image";

            image.style.maxWidth =
                "100%";

            image.style.borderRadius =
                "12px";

            image.style.marginTop =
                "8px";

            imageDiv.appendChild(
                image
            );

            chatBox.appendChild(
                imageDiv
            );

            chatBox.scrollTop =
                chatBox.scrollHeight;

            return;

        }


        /* Normal AI response */

        addMessage(
            data.reply ||
            "Sorry, NAD AI could not generate a response.",
            "bot"
        );


    } catch (error) {

        console.error(
            "CHAT ERROR:",
            error
        );

        const thinkingMessage =
            document.getElementById(
                thinkingId
            );

        if (thinkingMessage) {

            thinkingMessage.remove();

        }

        addMessage(
            "Sorry, NAD AI is not responding right now. Please try again.",
            "bot"
        );

    }

}


/* =========================================
ATTACHMENT
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
                        ) + "px";

                }
            );

        }


        /* =================================
        VOICE INPUT
        ================================= */

        const voiceButton =
            document.getElementById(
                "voice-button"
            );

        const userInput =
            document.getElementById(
                "user-input"
            );


        if (
            voiceButton &&
            userInput &&
            "webkitSpeechRecognition" in window
        ) {

            const recognition =
                new webkitSpeechRecognition();

            recognition.continuous =
                false;

            recognition.interimResults =
                false;

            recognition.lang =
                "en-US";


            voiceButton.addEventListener(
                "click",
                function () {

                    try {

                        recognition.start();

                        voiceButton.innerHTML =
                            "🔴";

                    } catch (error) {

                        console.log(
                            "Voice already started"
                        );

                    }

                }
            );


            recognition.onresult =
                function (event) {

                    const voiceText =
                        event.results[0][0]
                            .transcript;

                    userInput.value =
                        voiceText;

                };


            recognition.onerror =
                function () {

                    voiceButton.innerHTML =
                        "🎤";

                };


            recognition.onend =
                function () {

                    voiceButton.innerHTML =
                        "🎤";

                };

        }

        else if (voiceButton) {

            voiceButton.addEventListener(
                "click",
                function () {

                    alert(
                        "Voice recognition is not supported in this browser."
                    );

                }
            );

        }

    }
);
