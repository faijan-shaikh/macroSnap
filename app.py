import json
from google import genai
from google.genai import types
import streamlit as st
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

from twilio.rest import Client as TwilioClient

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]
TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]

@st.cache_resource
def get_gemini_client():
    if not GEMINI_API_KEY:
        st.error("Missing GEMINI_API_KEY. Add it to .streamlit/secrets.toml")
        st.stop()
    return genai.Client(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_twilio_client():
    return TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

twilio_client = get_twilio_client()
gemini_client = get_gemini_client()
MODEL_NAME = "gemini-2.5-flash"

def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."
    text = " ".join(text.split())
    return text[:1500] + "..." if len(text) > 1500 else text

def send_whatsapp(to_number, user_name, summary):
    try:
        content_variables = json.dumps(
            {"1": user_name, "2": clean_whatsapp_text(summary)}, ensure_ascii=False
        )
        message = twilio_client.messages.create(
            from_ = TWILIO_WHATSAPP_FROM,
            to = f"whatsapp:{to_number}",
            content_sid = TWILIO_CONTENT_SID,
            content_variables = content_variables,
        )
        return True, message.sid
    except Exception as e:
        return False, str(e)


if "conversation_contents" not in st.session_state:
    st.session_state.conversation_contents = []

def render_messages(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])

def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_messages(st.session_state.messages[-1])

def ask_gemini(parts):
    try:
        user_content = types.Content(
            role="user",
            parts=[
                part if isinstance(part, types.Part) else types.Part.from_text(text=part)
                for part in parts
            ],
        )
        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=[*st.session_state.conversation_contents, user_content],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        if response.text is None:
            raise RuntimeError("Gemini returned no text response.")
        st.session_state.conversation_contents.extend(
            [
                user_content,
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.text)],
                ),
            ]
        )
        return response.text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"
    
# step 1: onboarding (username and phone number)

if 'onboarded' not in st.session_state:
    st.title("Nutrition 🥗")
    st.markdown("Snap it, track it, see yourself the results!")

    with st.form("onboarding_form"):
        name = st.text_input("Enter your name")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code, e.g., +1 123 456 7890)",
            placeholder="+91XXXXXXXXXX",
            help="Please enter your WhatsApp number with the country code.",
        )

        submit_button = st.form_submit_button("Let's go 🚀")

    if submit_button:
        if not name.strip() or not whatsapp_number.strip():
            st.error("Please fill in both fields.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            st.session_state.messages = []
            st.session_state.conversation_contents = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

# create a chat interface 

header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("Nutrition 🥗")

with button_col:
    if st.button("Send to WhatsApp", use_container_width=True):
        has_user_messages = any(
            message["role"] == "user" for message in st.session_state.messages
        )
        if not has_user_messages:
            st.warning("Track at least one meal or ask a nutrition question first.")
        else:
            # send the chat messages to WhatsApp
            with st.spinner("Summarizing your day..."):
                summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            success, info = send_whatsapp(
                st.session_state.whatsapp_number,
                st.session_state.name,
                summary,
            )
            if success:
                st.success("Sent! Check your WhatsApp.")
            else:
                st.error(f"Couldn't send to WhatsApp: {info}")

st.caption(f"Logged in as: {st.session_state.name} - updates go to WhatsApp: {st.session_state.whatsapp_number}")

if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_messages(message)

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal!",
    accept_file = True,
    file_type = ["image/png", "image/jpeg", "image/jpg"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text 
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("What's this meal?  Give me the calories, macros.")

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)
    