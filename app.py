import streamlit as st
st.set_page_config(page_title="HelpMeDoc", layout="centered")
st.write("✅ App started")
from dotenv import load_dotenv
import os
from openai import OpenAI
from chat import run_chat_interface
from ocr import run_ocr_interface
from hospital import run_hospital_finder

with st.sidebar:
    st.header("👤 User Profile")
    user_age = st.number_input("Age", min_value=1, max_value=120, step=1)
    user_gender = st.selectbox("Gender", ["Not specified", "Male", "Female", "Other"])
    is_pregnant = st.checkbox("Pregnant", value=False)
    user_language = st.selectbox("Preferred Language", ["English", "Vietnamese", "Chinese"])


st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.image("assets/dori.png", width=150, caption="Dori, your AI medical assistant 🦉")
st.markdown("Get help with symptoms, hospital navigation, and medication instructions.")

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

menu = st.sidebar.selectbox("Choose a service", ["💬 Chat with Dori", "💊 Interpret Medication Image", "🏥 Hospital Finder"])

user_info = {
    "age": user_age,
    "gender": user_gender,
    "pregnant": is_pregnant,
    "language": user_language
}
st.sidebar.write("✅ 메뉴 로딩 중...")
if menu == "💬 Chat with Dori":
    run_chat_interface(client, user_info=user_info)
elif menu == "💊 Interpret Medication Image":
    run_ocr_interface(client)
elif menu == "🏥 Hospital Finder":
    run_hospital_finder()

