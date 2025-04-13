import streamlit as st
import pandas as pd
import os
import numpy as np
import easyocr
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium
def display_medication_cards(text):
    for block in text.strip().split("\n\n"):
        if block.strip():
            st.markdown(f"""
            <div style='
                background-color: #e6f2f1;
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 10px;
                font-size: 16px;
            '>
            {block.strip().replace("\\n", "<br>")}
            </div>
            """, unsafe_allow_html=True)

# 설정
st.set_page_config(page_title="HelpMeDoc", layout="centered")
st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.image("dori.png", width=150, caption="Dori, your AI medical assistant 🦉")
st.markdown("Get help with symptoms, hospital navigation, and medication instructions.")

# 환경변수 로딩
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 사이드바 메뉴
menu = st.sidebar.selectbox("Choose a service", ["💬 Chat with Dori", "💊 Interpret Medication Image", "🏥 Hospital Finder"])

# 병원 데이터 불러오기
@st.cache_data
def load_hospital_data():
    path = "hospital_sample.csv"
    if not os.path.exists(path):
        st.error("🚨 hospital_sample.csv 파일이 존재하지 않습니다.")
        return pd.DataFrame()
    return pd.read_csv(path)

# 💬 Chatbot
if menu == "💬 Chat with Dori":
    user_input = st.text_input("Ask Dori about symptoms, clinics, or emergencies...")

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
                response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                with st.container():
                    col1, col2 = st.columns([1, 9])
                    with col1:
                        st.image("dori_2d.png", width=50)
                    with col2:
                        st.markdown(f"""
                        <div style='
                            background-color: #d1f3ef;
                            padding: 12px 16px;
                            border-radius: 12px;
                            margin-top: 4px;
                            font-size: 16px;
                            line-height: 1.5;
                        '>
                        {response.choices[0].message.content}
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"GPT Error: {e}")

# 💊 OCR 해석
elif menu == "💊 Interpret Medication Image":
    st.markdown("### 📷 약 사진 촬영 가이드")
    st.info("""
- 빛 반사 없이 찍어주세요  
- 종이를 펼쳐서 정면에서 찍어주세요  
- 텍스트가 잘 보이게 확대해주세요  
- 표 전체보다 '약 정보가 있는 부분' 중심으로 찍는 것이 더 정확합니다
    """)

    uploaded_file = st.file_uploader("Upload your medication image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            image_np = np.array(image)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            reader = easyocr.Reader(['ko'], gpu=False)
            result = reader.readtext(image_np, detail=0)
            text = " ".join(result)

            messages = [
                {"role": "system", "content": "You are an assistant that helps foreigners understand Korean medication instructions.\n"
                        "You will receive text extracted from an image using OCR.\n\n"
                        "Please:\n"
                        "- Identify each drug name separately\n"
                        "- For each drug, list: the drug name, purpose, dosage instructions (e.g., how many times per day), and storage method\n"
                        "- Translate only the essential information clearly and simply\n"
                        "- If any part is unclear, say 'not clearly recognized'\n"
                        "- Do not change the drug names. Do not guess unknown drugs\n"
                        "- Be very cautious with dosage and purpose. Do not invent anything."},
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
# 🏥 병원 탐색
elif menu == "🏥 Hospital Finder":
    df = load_hospital_data()
    if df.empty:
        st.warning("No hospital data found.")
    else:
        st.subheader("🏥 병원 탐색")
        region = st.text_input("지역을 입력하세요 (예: 서울, 경기, 부산)", "")
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
