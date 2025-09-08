import streamlit as st
from groq import Groq
import requests
from bs4 import BeautifulSoup
import datetime

# -------------------------------
# Fetch website text with BeautifulSoup
# -------------------------------
def get_website_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:4000]  # trim for token limit
    except Exception as e:
        return f"Error fetching website: {str(e)}"

# -------------------------------
# Get AI response from Groq using website context
# -------------------------------
def get_response(hotel_text, chat_history, model_id="llama-3.1-8b-instant"):
    try:
        groq_api_key = st.secrets["groq_api_key"]
        client = Groq(api_key=groq_api_key)

        # Start with system prompt and hotel text
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant answering questions based "
                    "on the following hotel information:\n" + hotel_text
                ),
            }
        ]

        # Add all chat messages (user + assistant) after system + hotel context
        messages.extend(chat_history)

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=1,
            
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------
# Streamlit app setup
# -------------------------------
st.set_page_config(page_title="Hotel Info Chatbot", page_icon="🏨", layout="wide")

st.markdown("""
<style>
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f9fafb;
}
.user-container {
    text-align: right;
    margin-bottom: 12px;
}
.user-message {
    display: inline-block;
    background-color: #0b93f6;
    color: white;
    padding: 10px 16px;
    border-radius: 18px 18px 0 18px;
    max-width: 70%;
    word-wrap: break-word;
}
.assistant-container {
    text-align: left;
    margin-bottom: 12px;
}
.assistant-message {
    display: inline-block;
    background-color: #e5e5ea;
    color: #000;
    padding: 10px 16px;
    border-radius: 18px 18px 18px 0;
    max-width: 70%;
    word-wrap: break-word;
}
.stButton button {
    border-radius: 8px;
    padding: 0.5em 1em;
    font-weight: 600;
    background-color: #0b93f6;
    color: white;
    border: none;
}
.stButton button:hover {
    background-color: #0a7bdc;
    color: white;
}
.stTextInput > div > div > input {
    border-radius: 12px;
    padding: 0.75em 1em;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🏨 Hotel Info Chatbot")
st.caption("Enter the URL of a hotel website, then ask anything about it!")

# URL input
hotel_url = st.text_input("Enter Hotel URL:", value="https://sriraghavendrahotel.com/")

# # Initialize session states
# if "hotel_text" not in st.session_state:
#     st.session_state.hotel_text = ""

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# if hotel_url and (st.session_state.hotel_text == "" or st.session_state.hotel_text.startswith("Error")):
#     st.info("Fetching hotel data...")
#     st.session_state.hotel_text = get_website_text(hotel_url)
#     if st.session_state.hotel_text.startswith("Error"):
#         st.error(st.session_state.hotel_text)
#     else:
#         st.success("Hotel data loaded successfully!")



# Initialize session states
if "hotel_text" not in st.session_state:
    st.session_state.hotel_text = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Fetch hotel text silently (no UI message)
if hotel_url and (st.session_state.hotel_text == "" or st.session_state.hotel_text.startswith("Error")):
    hotel_text_result = get_website_text(hotel_url)
    
    # Still store it in session
    st.session_state.hotel_text = hotel_text_result

    # You can optionally log error (for debugging)
    if hotel_text_result.startswith("Error"):
        print("⚠️ Error loading hotel text:", hotel_text_result)

# User input for chat
user_input = st.chat_input("Ask me about the hotel...")

if user_input:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get AI response based on hotel_text and chat history
    response = get_response(st.session_state.hotel_text, st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display chat messages
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"<div class='user-container'><div class='user-message'>{chat['content']}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-container'><div class='assistant-message'>{chat['content']}</div></div>", unsafe_allow_html=True)

# Chat controls
st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.hotel_text = ""

with col2:
    def export_chat():
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"hotel_chat_export_{now}.txt"
        chat_lines = []
        for msg in st.session_state.chat_history:
            role = "You" if msg["role"] == "user" else "Bot"
            chat_lines.append(f"{role}: {msg['content']}\n")
        return filename, "\n".join(chat_lines)

    if st.button("📤 Export Chat", use_container_width=True):
        filename, chat_text = export_chat()
        st.download_button(
            label="Download Chat as .txt",
            data=chat_text,
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )



