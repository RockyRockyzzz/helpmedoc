import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import easyocr
from PIL import Image
import os
import re
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

@st.cache_data
def load_hospital_data():
    path = "hospital_sample.csv"
    if not os.path.exists(path):
        st.error("🚨 병원 데이터 파일(hospital_sample.csv)을 찾을 수 없습니다.")
        return pd.DataFrame()
    return pd.read_csv(path)

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="HelpMeDoc", layout="centered")

st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.image("dori.png", width=150, caption="Dori, your AI medical assistant 🦉")

menu = st.sidebar.selectbox("Choose a service", ["💬 Chat with Dori", "💊 Interpret Medication Image", "🏥 병원 탐색"])

def display_medication_cards(gpt_text):
    drugs = re.split(r"(?=Drug name:)", gpt_text.strip())

    for drug in drugs:
        lines = drug.strip().splitlines()
        if not lines or not lines[0].startswith("Drug name:"):
            continue

        name = lines[0].replace("Drug name:", "").strip()
        purpose = dosage = storage = "Not specified"

        for line in lines[1:]:
            if "Purpose:" in line:
                purpose = line.replace("Purpose:", "").strip()
            elif "Dosage instructions:" in line:
                dosage = line.replace("Dosage instructions:", "").strip()
            elif "Storage method:" in line:
                storage = line.replace("Storage method:", "").strip()

        with st.container():
            st.markdown("----")
            st.subheader(f"💊 {name}")
            st.markdown(f"**📌 Purpose:** {purpose}")
            st.markdown(f"**🕐 Dosage:** {dosage}")
            st.markdown(f"**📦 Storage:** {storage}")

if menu == "💬 Chat with Dori":
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
This should be shown even if the user doesn’t specify a region.

For symptoms, follow a triage guideline similar to the Korean Triage and Acuity Scale (KTAS).
Classify into:
1. Emergency – Recommend 응급실 if symptoms include chest pain, severe pain, vomiting with fever, confusion, loss of consciousness, or danger signs in elderly, children, or pregnancy.
2. Concerning – Recommend clinic within 24h for symptoms like moderate pain, ongoing fever, worsening conditions.
3. Mild – Suggest monitoring and clinic if no improvement in 1–2 days.

Always remind the user this is not a medical diagnosis and they should seek help if unsure.
"""
            },
            {"role": "user", "content": user_input}
        ]

        with st.spinner("Dori is thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                st.success("Dori's Response:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"GPT Error: {e}")

elif menu == "💊 Interpret Medication Image":
    st.markdown("### 📷 사진 촬영 가이드")
    st.info("""
- 빛 반사 없이 찍어주세요  
- 종이를 펼쳐서 정면에서 찍어주세요  
- 텍스트가 잘 보이게 확대해주세요  
- 표 전체보다 '약 정보가 있는 부분' 중심으로 찍는 것이 더 정확합니다
    """)

    uploaded_file = st.file_uploader("Upload a picture of your medication label", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            # OCR with EasyOCR
            with st.spinner("Extracting text using OCR..."):
                reader = easyocr.Reader(['ko'], gpu=False)
                result = reader.readtext(image, detail=0)
                text = "\n".join(result)

            st.subheader("📝 Detected Text from Image")
            st.code(text)

            st.subheader("💬 Explanation by Dori")
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that helps foreigners understand Korean medication instructions.\n"
                        "You will receive text extracted from an image using OCR.\n\n"
                        "Please:\n"
                        "- Identify each drug name separately\n"
                        "- For each drug, list: the drug name, purpose, dosage instructions (e.g., how many times per day), and storage method\n"
                        "- Translate only the essential information clearly and simply\n"
                        "- If any part is unclear, say 'not clearly recognized'\n"
                        "- Do not change the drug names. Do not guess unknown drugs\n"
                        "- Be very cautious with dosage and purpose. Do not invent anything."
                    )
                },
                {"role": "user", "content": text}
            ]
            with st.spinner("Dori is analyzing the image..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    )
                    st.success("💡 Dori's Explanation")
                    display_medication_cards(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"GPT Error: {e}")
        except Exception as e:
            st.error(f"OCR Error: {e}")
elif menu == "🏥 병원 탐색":
    df = load_hospital_data()
    if df.empty:
        st.warning("병원 데이터가 없습니다.")
    else:
        st.subheader("🏥 병원 탐색")
        region = st.text_input("지역 입력 (예: 서울, 경기, 부산)")
        department = st.selectbox("진료과목", ["전체", "내과", "정형외과"])

        filtered = df.copy()
        if region:
            filtered = filtered[filtered["주소"].str.contains(region)]
        if department != "전체":
            filtered = filtered[filtered["진료과목"] == department]

        st.markdown(f"🔍 총 {len(filtered)}개 병원 검색됨")

        if not filtered.empty:
            m = folium.Map(location=[filtered["위도"].mean(), filtered["경도"].mean()], zoom_start=12)
            for _, row in filtered.iterrows():
                folium.Marker(
                    location=[row["위도"], row["경도"]],
                    popup=f"{row['병원명']}<br>{row['주소']}",
                    tooltip=row["병원명"],
                ).add_to(m)
            st_folium(m, width=700, height=500)

        for _, row in filtered.iterrows():
            st.markdown(f"""**{row['병원명']}**  
{row['주소']}  
{row['전화번호']}  
[카카오맵으로 보기](https://map.kakao.com/?q={row['병원명']})  
---""")
