import streamlit as st
import numpy as np
import easyocr
from PIL import Image
from utils.display import display_medication_cards

def run_ocr_interface(client):
    st.subheader("💊 Interpret Medication Image")
    uploaded_file = st.file_uploader("Upload a medication label image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            image_np = np.array(image)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            reader = easyocr.Reader(['ko'], gpu=False)
            result = reader.readtext(image_np, detail=0)
            text = " ".join(result)
            messages = [
                {"role": "system", "content": "You are an assistant that helps foreigners understand Korean medication..."},
                {"role": "user", "content": text}
            ]
            with st.spinner("Dori is analyzing the image..."):
                try:
                    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                    st.text(response.choices[0].message.content)
                    display_medication_cards(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"GPT Error: {e}")
        except Exception as e:
            st.error(f"OCR Error: {e}")
