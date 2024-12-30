import streamlit as st
import edge_tts
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import asyncio
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Fetch API keys from environment variables
CHATGROQ_API_KEY = os.getenv("CHATGROQ_API_KEY")

# Initialize the ChatGroq model
llm = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.7,
    max_tokens=1500,
    timeout=10,  # Timeout for API requests
    max_retries=2,  # Number of retries for failed requests
    api_key=CHATGROQ_API_KEY
)

# Function to generate audio using Edge TTS
async def generate_audio(text):
    try:
        audio_path = "output.mp3"
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")  # Choose a neural voice
        await communicate.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# Initialize chat session in Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to generate responses using ChatGroq
def generate_ai_response(prompt):
    try:
        # Add user input to conversation history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Create a chat prompt template with the conversation history
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful and comprehensive music tutor. You will provide detailed instructions, practice sessions, and exercises without referring to any external courses or materials. Your goal is to be the only teaching source for the student.")
            ] + [
                (entry["role"], entry["content"]) for entry in st.session_state.chat_history
            ]
        )

        # Generate the response
        response = (chat_prompt | llm).invoke({})

        # Add AI response to conversation history
        st.session_state.chat_history.append({"role": "ai", "content": response.content})

        # Extract and return the response content
        return response.content
    except Exception as e:
        return f"Unexpected error: {e}"

# Function to stream text one word at a time
def stream_text(text, container):  # Stream text character by character  # Preserve spaces and format
    characters = list(text)  # Break text into individual characters, preserving spaces  # Preserve original spacing, including multiple spaces
    streamed_text = ""
    for word in characters:
        streamed_text += word  # Add one character at a time  # Add words preserving spacing
        container.markdown(f"<div style='line-height: 1.5;'>{streamed_text}</div>", unsafe_allow_html=True)  # Ensure proper streaming
        time.sleep(0.01)  # Adjust speed of streaming

# Streamlit App
st.set_page_config(page_title="AI Music Mentor", page_icon="🎵", layout="wide", initial_sidebar_state="collapsed")

# Add a background image for the UI and set dark mode
st.markdown(
    """
    <style>
    body {
        background-image: url('https://example.com/musical-background.jpg');
        background-size: cover;
        background-color: black;
        color: black;
    }
    .stMarkdown {
        color: black !important;
    }
    .st-chat-message {
        color: #1DB954 !important;  /* Spotify green for messages */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and header with a musical theme
st.title("🎵 AI Music Mentor")
st.header("Your personal AI tutor for all things music 🎶")

# Display chat history
st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "ai":
            st.markdown(f"<div style='color: #1DB954;'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color: #1DB954;'>{message['content']}</div>", unsafe_allow_html=True)

user_prompt = st.chat_input("Type your question or share your progress here 🎹:")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Show a spinner animation while processing
    with st.spinner("Creating your musical guidance..."):
        # Get AI response
        ai_response = generate_ai_response(user_prompt)

        # Generate audio
        audio_path = asyncio.run(generate_audio(ai_response))

    # Add AI response to chat, play audio, and stream text
    if audio_path:
        with st.chat_message("ai"):
            st.audio(audio_path, format="audio/mp3", start_time=0)
            placeholder = st.empty()  # Placeholder for streaming text
            stream_text(ai_response, placeholder)
