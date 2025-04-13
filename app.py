import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="HelpMeDoc", layout="centered")

st.title("💬 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.markdown("Get help with symptoms, hospital navigation, and medication instructions.")

menu = st.sidebar.selectbox("Choose a service", ["🩺 Chat with GPT", "💊 Interpret Medication Image"])

if menu == "🩺 Chat with GPT":
    user_input = st.text_input("Type your medical-related question here (in English)...")
    if user_input:
        messages = [
            {"role": "system", "content": "You are a helpful Korean medical chatbot for foreigners. Answer in simple English. Do not make medical diagnoses."},
            {"role": "user", "content": user_input}
        ]
        with st.spinner("GPT is typing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages
                )
                st.success("Response:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

elif menu == "💊 Interpret Medication Image":
    uploaded_file = st.file_uploader("Upload a picture of your medication label", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        text = pytesseract.image_to_string(image)
        st.subheader("📝 Detected Text")
        st.code(text)
        st.subheader("💬 GPT Explanation")
        messages = [
            {"role": "system", "content": "You are an assistant that explains Korean medication instructions to foreigners in simple English. Do not change the dosage, just explain clearly."},
            {"role": "user", "content": text}
        ]
        with st.spinner("GPT is typing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages
                )
                st.success("Response:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")