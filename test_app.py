import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
from chat import run_chat_interface
from ocr import run_ocr_interface
from hospital import run_hospital_finder

st.set_page_config(page_title="HelpMeDoc", layout="centered")
st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.image("assets/dori.png", width=150, caption="Dori, your AI medical assistant 🦉")
st.markdown("Get help with symptoms, hospital navigation, and medication instructions.")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

menu = st.sidebar.selectbox("Choose a service", ["💬 Chat with Dori", "💊 Interpret Medication Image", "🏥 Hospital Finder"])

if menu == "💬 Chat with Dori":
    run_chat_interface(client)
elif menu == "💊 Interpret Medication Image":
    uploaded_file = st.file_uploader("Upload your image", type=["jpg", "png"])
    run_ocr_interface(client)
elif menu == "🏥 Hospital Finder":
    run_hospital_finder()
