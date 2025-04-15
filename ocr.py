import streamlit as st
import numpy as np
import easyocr
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from fuzzywuzzy import fuzz
from PIL import Image
from utils.display import display_medication_cards

SERVICE_KEY = "O0wI7BmTCPHgoS8Trmp9INLhy1qVqdWR/wUaKnlnTDeY/ZNsc4wrkOqolStMSZoHjdjJ8GEoL1MxqmGyMc6vxA=="
ENCODED_KEY = urllib.parse.quote(SERVICE_KEY, safe='')

def fetch_drug_list(keyword, max_rows=10):
    keyword = keyword.strip()
    if not keyword:
        return []

    url = f"https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
    full_url = f"{url}?serviceKey={ENCODED_KEY}&itemName={urllib.parse.quote(keyword)}&pageNo=1&numOfRows={max_rows}"

    try:
        res = requests.get(full_url, timeout=5)
        res.raise_for_status()
        root = ET.fromstring(res.text)
        names = [item.findtext("itemName").strip() for item in root.iter("item") if item.findtext("itemName")]
        return names
    except Exception as e:
        print("❌ fetch_drug_list error:", e)
        return []

def get_best_match(ocr_text, drug_list):
    best_score = 0
    best_match = None
    for name in drug_list:
        score = fuzz.ratio(ocr_text, name)
        if score > best_score:
            best_score = score
            best_match = name
    return best_match, best_score

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
✅ We recommend opening the photo and taking a screenshot before uploading.""")
    uploaded_file = st.file_uploader("Upload a medication label image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            image_np = np.array(image)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            reader = easyocr.Reader(['ko'], gpu=False)
            result = reader.readtext(image_np, detail=0)
            text = " ".join(result)
            # 2. 약물명 유사도 기반 정제
            drug_list = fetch_drug_list(text)
            best_match, score = get_best_match(text, drug_list)

            # 3. GPT에 넘길 약 이름 구성
            if score >= 90:
                drug_name = best_match
            elif score >= 70:
                drug_name = f"{text} (possibly: {best_match})"
            else:
                drug_name = f"{text} (possibly: unknown)"
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
 """

                        },
                {"role": "user", "content": drug_name}
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
