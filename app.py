import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import os

# Set tesseract command path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="HelpMeDoc", layout="centered")

st.title("HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.markdown("Get help with symptoms, hospital navigation, and medication instructions.")

menu = st.sidebar.selectbox("Choose a service", ["Chat with Dori", "Interpret Medication Image"])

if menu == "Chat with Dori":
    user_input = st.text_input("Type your medical-related question here (in English)...")
    if user_input:
        messages = [
            {
                "role": "system",
                "content": """You are a friendly and knowledgeable medical assistant helping foreigners living in Korea. 
You help them understand symptoms in simple English, and tell them which department (진료과) to visit at a Korean hospital. 
Give clear, non-diagnostic guidance and practical tips like what kind of clinic to visit, how to say symptoms in Korean, and whether it's urgent. 
Do not make medical diagnoses or suggest medications. Avoid suggesting generic home remedies unless no other option is relevant. 

If you mention or recommend any department (진료과), such as 내과 (internal medicine), 정형외과 (orthopedic), 피부과 (dermatology), etc., ALWAYS include a clickable Kakao Map link in the format:
https://map.kakao.com/?q=진료과명 
(e.g. https://map.kakao.com/?q=내과). 
This should be shown even if the user doesn’t specify a region."""
            },
            {"role": "user", "content": user_input}
        ]
        with st.spinner("GPT is typing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                st.success("Response:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

elif menu == "Interpret Medication Image":
    uploaded_file = st.file_uploader("Upload a picture of your medication label", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            text = pytesseract.image_to_string(image)
            st.subheader("Detected Text")
            st.code(text)
            st.subheader("GPT Explanation")
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that explains Korean medication instructions to foreigners in simple English. "
                        "Do not change the dosage, just explain clearly what the instructions mean."
                    )
                },
                {"role": "user", "content": text}
            ]
            with st.spinner("GPT is typing..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    )
                    st.success("Response:")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"GPT Error: {e}")
        except Exception as e:
            st.error(f"OCR Error: {e}")