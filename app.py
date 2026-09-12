from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson import ObjectId
from google import genai
from tavily import TavilyClient
import certifi
from datetime import datetime
import os


# ==========================================
# NAD AI - FLASK APPLICATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

bcrypt = Bcrypt(app)


# ==========================================
# MONGODB CONNECTION
# ==========================================

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000
)

try:

    client.admin.command("ping")

    print("MongoDB Connected Successfully!")

except Exception as e:

    print("MongoDB Connection Error:")
    print(e)


# ==========================================
# DATABASE AND COLLECTIONS
# ==========================================

db = client["nad_ai_database"]

users_collection = db["users"]

conversations_collection = db["conversations"]

messages_collection = db["messages"]


# ==========================================
# GEMINI AI CONNECTION
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================
# TAVILY WEB SEARCH CONNECTION
# ==========================================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ==========================================
# CHECK WHETHER WEB SEARCH IS NEEDED
# ==========================================

def needs_web_search(message):

    message_lower = message.lower()

    web_keywords = [
        "current",
        "now",
        "today",
        "latest",
        "recent",
        "news",
        "update",
        "this week",
        "this month",
        "who is the cm",
        "who is cm",
        "chief minister",
        "prime minister",
        "president",
        "minister",
        "election",
        "result",
        "weather",
        "price",
        "stock",
        "share price",
        "exchange rate",
        "distance",
        "train",
        "bus",
        "flight",
        "opening time",
        "closing time"
    ]

    for keyword in web_keywords:

        if keyword in message_lower:

            return True

    return False


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(
            url_for("chat_page")
        )

    return redirect(
        url_for("login")
    )


# ==========================================
# SIGNUP
# ==========================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            return render_template(
                "signup.html",
                error="Please fill all fields!"
            )

        existing_user = users_collection.find_one(
            {
                "email": email
            }
        )

        if existing_user:

            return render_template(
                "signup.html",
                error="Email already exists! Please login."
            )

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        result = users_collection.insert_one(
            {
                "email": email,
                "password": hashed_password,
                "created_at": datetime.now()
            }
        )

        session["user_id"] = str(
            result.inserted_id
        )

        session["email"] = email

        print(
            "New user saved successfully!"
        )

        return redirect(
            url_for("chat_page")
        )

    return render_template(
        "signup.html"
    )


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = users_collection.find_one(
            {
                "email": email
            }
        )

        if user and bcrypt.check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = str(
                user["_id"]
            )

            session["email"] = user["email"]

            print(
                "User logged in successfully!"
            )

            return redirect(
                url_for("chat_page")
            )

        return render_template(
            "login.html",
            error="Invalid email or password!"
        )

    return render_template(
        "login.html"
    )


# ==========================================
# CHAT PAGE
# ==========================================

@app.route("/chat")
def chat_page():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    try:

        conversations = list(
            conversations_collection.find(
                {
                    "user_id": session["user_id"]
                }
            ).sort(
                "updated_at",
                -1
            )
        )

    except Exception as e:

        print(
            "CHAT PAGE ERROR:",
            e
        )

        conversations = []

    return render_template(
        "chat.html",
        email=session.get(
            "email"
        ),
        conversations=conversations
    )


# ==========================================
# CREATE NEW CHAT
# ==========================================

@app.route("/api/new-chat", methods=["POST"])
def create_new_chat():

    if "user_id" not in session:

        return jsonify(
            {
                "error": "Unauthorized"
            }
        ), 401

    try:

        conversation = {
            "user_id": session["user_id"],
            "email": session["email"],
            "title": "New Chat",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = conversations_collection.insert_one(
            conversation
        )

        conversation_id = str(
            result.inserted_id
        )

        return jsonify(
            {
                "conversation_id": conversation_id,
                "title": "New Chat"
            }
        )

    except Exception as e:

        print(
            "NEW CHAT ERROR:",
            e
        )

        return jsonify(
            {
                "error": "Unable to create new chat"
            }
        ), 500


# ==========================================
# GET CHAT HISTORY
# ==========================================

@app.route("/api/chat/<conversation_id>")
def get_chat_history(conversation_id):

    if "user_id" not in session:

        return jsonify(
            {
                "error": "Unauthorized"
            }
        ), 401

    try:

        conversation = conversations_collection.find_one(
            {
                "_id": ObjectId(
                    conversation_id
                ),
                "user_id": session["user_id"]
            }
        )

        if not conversation:

            return jsonify(
                {
                    "error": "Chat not found"
                }
            ), 404

        messages = list(
            messages_collection.find(
                {
                    "conversation_id": conversation_id,
                    "user_id": session["user_id"]
                }
            ).sort(
                "created_at",
                1
            )
        )

        message_list = []

        for message in messages:

            message_list.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

        return jsonify(
            {
                "conversation_id": conversation_id,
                "title": conversation.get(
                    "title",
                    "New Chat"
                ),
                "messages": message_list
            }
        )

    except Exception as e:

        print(
            "CHAT HISTORY ERROR:",
            e
        )

        return jsonify(
            {
                "error": "Unable to load chat"
            }
        ), 500


# ==========================================
# ASK GEMINI
# ==========================================

@app.route("/api/chat", methods=["POST"])
def ask_gemini():

    # ======================================
    # CHECK LOGIN
    # ======================================

    if "user_id" not in session:

        return jsonify(
            {
                "error": "Unauthorized"
            }
        ), 401


    # ======================================
    # GET DATA
    # ======================================

    data = request.get_json(
        silent=True
    ) or {}

    user_message = data.get(
        "message",
        ""
    ).strip()

    conversation_id = data.get(
        "conversation_id",
        ""
    )


    # ======================================
    # CHECK EMPTY MESSAGE
    # ======================================

    if not user_message:

        return jsonify(
            {
                "error": "Message cannot be empty"
            }
        ), 400


    # ======================================
    # CREATE OR CHECK CONVERSATION
    # ======================================

    if not conversation_id:

        try:

            conversation = {
                "user_id": session["user_id"],
                "email": session["email"],
                "title": user_message[:40],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            result = conversations_collection.insert_one(
                conversation
            )

            conversation_id = str(
                result.inserted_id
            )

        except Exception as e:

            print(
                "CONVERSATION CREATE ERROR:",
                e
            )

            return jsonify(
                {
                    "error": "Unable to create conversation"
                }
            ), 500

    else:

        try:

            conversation = conversations_collection.find_one(
                {
                    "_id": ObjectId(
                        conversation_id
                    ),
                    "user_id": session["user_id"]
                }
            )

            if not conversation:

                return jsonify(
                    {
                        "error": "Conversation not found"
                    }
                ), 404

        except Exception as e:

            print(
                "INVALID CONVERSATION ERROR:",
                e
            )

            return jsonify(
                {
                    "error": "Invalid conversation ID"
                }
            ), 400


    # ======================================
    # GET PREVIOUS MESSAGES FOR AI MEMORY
    # ======================================

    try:

        previous_messages = list(
            messages_collection.find(
                {
                    "conversation_id": conversation_id,
                    "user_id": session["user_id"]
                }
            ).sort(
                "created_at",
                1
            )
        )

        previous_messages = previous_messages[-10:]

        conversation_text = ""

        for message in previous_messages:

            content = message.get(
                "content",
                ""
            )[:1000]

            if message["role"] == "user":

                conversation_text += (
                    "User: "
                    + content
                    + "\n"
                )

            else:

                conversation_text += (
                    "NAD AI: "
                    + content
                    + "\n"
                )

        conversation_text += (
            "User: "
            + user_message[:2000]
        )

    except Exception as e:

        print(
            "MEMORY LOAD ERROR:",
            e
        )

        conversation_text = (
            "User: "
            + user_message[:2000]
        )


    # ======================================
    # TAVILY WEB SEARCH
    # ======================================

    search_context = ""

    if needs_web_search(user_message):

        try:

            search_response = tavily_client.search(
                query=user_message,
                search_depth="basic",
                max_results=2
            )

            for result in search_response.get(
                "results",
                []
            ):

                title = result.get(
                    "title",
                    ""
                )

                content = result.get(
                    "content",
                    ""
                )[:1500]

                search_context += (
                    "Title: "
                    + title
                    + "\n"
                    + "Content: "
                    + content
                    + "\n\n"
                )

        except Exception as e:

            print(
                "TAVILY ERROR:",
                e
            )

            search_context = ""


    # ======================================
    # GET RESPONSE FROM GEMINI
    # ======================================

    try:

        if search_context:

            prompt = (
                "You are NAD AI, a helpful and friendly AI assistant.\n\n"

                "IMPORTANT WEB SEARCH RULE:\n"
                "The user asked a question that may require current or "
                "recent information. Web search results are provided below.\n"
                "Use the web search results as the primary source for "
                "current facts.\n"
                "Do not answer a current-fact question using old memory "
                "when the web results provide a newer answer.\n"
                "If the web results are unclear or conflicting, say that "
                "the information could not be verified clearly.\n\n"

                "If the user asks in Tamil or Tanglish, respond in "
                "simple Tamil or Tanglish.\n\n"

                "WEB SEARCH RESULTS:\n"
                + search_context
                + "\n"

                "CONVERSATION:\n"
                + conversation_text
            )

        else:

            prompt = (
                "You are NAD AI, a helpful and friendly AI assistant.\n\n"

                "Continue the conversation naturally.\n"
                "Answer clearly and accurately.\n"
                "If the user asks in Tamil or Tanglish, respond in "
                "simple Tamil or Tanglish.\n\n"

                "CONVERSATION:\n"
                + conversation_text
            )


        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        bot_reply = response.text

        if not bot_reply:

            bot_reply = (
                "Sorry, NAD AI could not generate a response."
            )

    except Exception as e:

        print(
            "GEMINI ERROR:",
            e
        )

        return jsonify(
            {
                "reply": (
                    "Sorry, NAD AI is not responding right now. "
                    "Please try again."
                ),
                "conversation_id": conversation_id
            }
        ), 500


    # ======================================
    # SAVE MESSAGES TO DATABASE
    # ======================================

    try:

        messages_collection.insert_one(
            {
                "conversation_id": conversation_id,
                "user_id": session["user_id"],
                "role": "user",
                "content": user_message,
                "created_at": datetime.now()
            }
        )

        messages_collection.insert_one(
            {
                "conversation_id": conversation_id,
                "user_id": session["user_id"],
                "role": "assistant",
                "content": bot_reply,
                "created_at": datetime.now()
            }
        )

        conversation_data = conversations_collection.find_one(
            {
                "_id": ObjectId(
                    conversation_id
                ),
                "user_id": session["user_id"]
            }
        )

        if conversation_data["title"] == "New Chat":

            conversations_collection.update_one(
                {
                    "_id": ObjectId(conversation_id),
                    "user_id": session["user_id"]
                },
                {
                    "$set": {
                        "title": user_message[:40],
                        "updated_at": datetime.now()
                    }
                }
            )

        else:

            conversations_collection.update_one(
                {
                    "_id": ObjectId(conversation_id),
                    "user_id": session["user_id"]
                },
                {
                    "$set": {
                        "updated_at": datetime.now()
                    }
                }
            )

        print(
            "Messages saved to MongoDB!"
        )

    except Exception as e:

        print(
            "MONGODB SAVE ERROR:",
            e
        )


    # ======================================
    # SEND RESPONSE TO WEBSITE
    # ======================================

    return jsonify(
        {
            "reply": bot_reply,
            "conversation_id": conversation_id
        }
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
