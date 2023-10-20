from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
from gtts import gTTS
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Define a function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text)
    tts.save("output.mp3")
    st.audio("output.mp3")

# Define a function to convert speech to text
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
        st.write("Processing...")
    try:
        user_input = r.recognize_google(audio)
        st.text(f'YOU: {user_input}')
        return user_input
    except sr.UnknownValueError:
        st.write("Oops, I didn't get your audio, Please try again.")
        return None

# Initialize session state variable
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

# Initialize the ChatOpenAI model
openapi_key = st.secrets["YOUR_OPENAI_API_KEY"]
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key=openapi_key,
    max_tokens=100
)

# Define a function to generate response
def generate_response(user_query):
    # Build the list of messages
    zipped_messages = build_message_list(user_query)

    # Generate response using the chat model
    ai_response = chat(zipped_messages)

    response = ai_response.content

    return response

# Define a function to build a message list
def build_message_list(user_query):
    """
    Build a list of messages including system, human, and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        content="""Your name is Voice Text Assistant. You are an AI Technical Expert for Artificial Intelligence, here to guide and assist students with their AI-related questions and concerns. Please provide accurate and helpful information, and always maintain a polite and professional tone.

(Your introductory message here...)"""
    )]

    # Zip together the past and generated messages
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(
                content=human_msg))  # Add user messages
        if ai_msg is not None:
            zipped_messages.append(
                AIMessage(content=ai_msg))  # Add AI messages

    zipped_messages.append(HumanMessage(content=user_query))  # Add the latest user message

    return zipped_messages

# Set streamlit page configuration
st.set_page_config(page_title="text and aduio bots")
st.title("text to voice bot")

# Add a 'Speak' button for voice input
input_option = st.radio("Select Input Method:", ["Text", "Audio"])
user_input = ""

# Define a function to display the conversation history for text input in newest to oldest order
def display_text_conversation_history():
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        if i < len(st.session_state["past"]):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '-text-user')
        message(st.session_state["generated"][i], key=str(i) + '-text')

# Define a function to display the conversation history for audio input in newest to oldest order
def display_audio_conversation_history():
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        if i < len(st.session_state["past"]):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '-audio-user')
        message(st.session_state["generated"][i], key=str(i) + '-audio')

if input_option == "Text":
    user_input = st.text_input("Enter your message:")
    if st.button("Submit"):
        if user_input:
            # Append user query to past queries
            st.session_state.past.append(user_input)

            # Generate response
            output = generate_response(user_input)

            # Append AI response to generated responses
            st.session_state.generated.append(output)

            # Display user and AI messages
            #st.text(f'YOU: {user_input}')
            text_to_speech(output)
            # Display the conversation history for text input
            display_text_conversation_history()

elif input_option == "Audio":
    if st.button('Talk to Me'):
        user_input = speech_to_text()

        if user_input:
            # Append user query to past queries
            st.session_state.past.append(user_input)

            # Generate response
            output = generate_response(user_input)

            # Append AI response to generated responses
            st.session_state.generated.append(output)

            # Display user and AI messages
            #st.text(f'YOU: {user_input}')
            text_to_speech(output)

# Display the conversation history for audio input
            display_audio_conversation_history()
