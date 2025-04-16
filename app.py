import streamlit as st
st.set_page_config(page_title="HelpMeDoc-Your AI Health Assistant", layout="centered")
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

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #E0F7FA;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("assets/dori.png", width=160)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("Get help with symptoms, hospital navigation, and medication instructions.")
