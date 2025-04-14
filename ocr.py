import streamlit as st
import numpy as np
import easyocr
from PIL import Image
from utils.display import display_medication_cards

def run_ocr_interface(client):
    st.subheader("💊 Interpret Medication Image")
    st.markdown("### 📷 Upload Guide")
    st.info("""
- Take a photo clearly under good lighting
- Avoid shadows and blur
- Make sure the label is readable and centered
- ✅ Only JPG, JPEG, PNG formats are supported
- ⚠️ **iPhone users:**  
Photos taken with the default camera are in HEIC format and may not upload properly.  
✅ We recommend opening the photo and taking a screenshot before uploading.
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
                {"role": "system", "content": "You are an assistant that helps foreigners understand Korean medication instructions.\n"
                        "You will receive OCR text with potential recognition errors.\n"
                        "Correct the content and rewrite it clearly in a medication guide format, "
                        "showing drug names, dosage, purpose, cautions, and storage instructions.\n"
                        """  You will receive OCR-extracted Korean medication information.

Your job is to:
1. Extract the drug names exactly as they appear.
2. For each drug, if the name matches a real Korean medication, explain normally.
3. If the name seems slightly incorrect or misspelled, try to guess the most likely correct name.
4. In that case, clearly indicate that the name may be inaccurate.
5. Use this format for each drug:

Drug name: <OCR name> (possibly: <best guess>)  
Purpose: <explanation in English>  
Dosage instructions: <as extracted>  
Storage method: <if mentioned>

Only explain what can be reasonably inferred from the text. If unclear, say: 'not clearly recognized'.
 """},
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
