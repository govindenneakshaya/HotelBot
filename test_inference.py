from groq import Groq
import streamlit as st
import requests
from bs4 import BeautifulSoup

def get_website_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:4000]  # Keep it under token limit for LLMs
    except Exception as e:
        return f"Error fetching website: {str(e)}"

def get_response(hotel_text, user_question, model_id="llama-3.1-8b-instant"):
    try:
        groq_api_key = st.secrets["groq_api_key"]
        client = Groq(api_key=groq_api_key)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers questions based on hotel website content:\n"
                    + hotel_text
                ),
            },
            {"role": "user", "content": user_question},
        ]

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    hotel_url = "https://sriraghavendrahotel.com/"
    hotel_text = get_website_text(hotel_url)

    if hotel_text.startswith("Error"):
        print(hotel_text)
    else:
        question = "What are the dishes available in this hotel?"
        answer = get_response(hotel_text, question)

        print("\n🧠 Answer from Groq:")
        print(answer)
