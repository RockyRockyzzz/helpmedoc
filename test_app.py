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
def display_medication_cards(gpt_text):
    import streamlit as st
    import re

    # Split the text by each "Drug name" entry
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


# 설정
st.set_page_config(page_title="HelpMeDoc", layout="centered")
st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #E0F7FA;
    }
    </style>
""", unsafe_allow_html=True)


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
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #E0F7FA;
        }
        </style>
    """, unsafe_allow_html=True)

    # 버튼 스타일 + 입력창 + 제출 버튼
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #FFCCBC;
            color: #333333;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            font-size: 16px;
            transition: background-color 0.2s ease;
        }

        div.stButton > button:hover {
            background-color: #FFAB91;
        }

        div.stButton > button:active {
            background-color: #FF8A65;
        }
        </style>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([8, 1])  # 비율은 필요 시 조절 가능

    with col1:
        user_input = st.text_input("Ask Dori about symptoms, clinics, or emergencies...", label_visibility="collapsed", key="user_input")

    with col2:
        submitted = st.button("↑", use_container_width=True)

    if submitted and user_input:
    # GPT 응답 처리

        
        messages = [
            {
                "role": "system",
                "content": """You are a friendly and knowledgeable medical assistant helping foreigners living in Korea.
You help them understand symptoms in simple English, and tell them which department (진료과) to visit at a Korean hospital.
Give clear, non-diagnostic guidance and practical tips like what kind of clinic to visit, how to say symptoms in Korean, and whether it's urgent.
Do not make medical diagnoses or suggest medications. Avoid suggesting generic home remedies unless no other option is relevant.

If you mention or recommend any department (진료과), such as 내과 (internal medicine), 정형외과 (orthopedic), 피부과 (dermatology), **or 응급실 (emergency room)**, ALWAYS include a clickable Kakao Map link in the format:
https://map.kakao.com/?q=진료과명
(e.g. https://map.kakao.com/?q=내과 or https://map.kakao.com/?q=응급실).
This should be shown even if the user doesn’t specify a region.

Use triage guidance based on the Korean Triage and Acuity Scale (KTAS) and Korea's official list of emergency symptoms defined by law.

For symptoms, classify into:
1. Emergency – Recommend 응급실 (emergency room) if symptoms include:
   - Chest pain or pressure
   - Difficulty breathing
   - Severe or sudden abdominal pain
   - Loss of consciousness
   - Severe bleeding
   - Seizures or convulsions
   - High fever with vomiting or confusion
   - Any danger signs in elderly, children, or pregnant individuals
   - Symptoms of stroke (e.g. facial droop, slurred speech, limb weakness)
   - Severe trauma or burns
   These match emergency symptoms listed by Korean law.

2. Concerning – Recommend visiting a clinic within 24 hours if symptoms include:
   - Moderate pain or ongoing fever
   - Symptoms that are worsening or spreading
   - Persistent dizziness, mild shortness of breath
   - Early infection signs without high risk

3. Mild – Suggest home monitoring and visiting clinic if no improvement in 1–2 days.
   - Examples: mild sore throat, minor cough, fatigue, muscle aches

Always include this reminder:
"This is not a medical diagnosis. If unsure or symptoms worsen, visit a doctor or emergency room.
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

                        "If unclear, write 'uncertain' and avoid guessing new drug names."
                        "- Be very cautious with dosage and purpose. Do not invent anything."},
                {"role": "user", "content": text}
            ]
            with st.spinner("Dori is analyzing the image..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    )
                    st.text(response.choices[0].message.content)
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
        st.subheader("🏥 Hospital Finder")

        # English label → Korean value mapping
        department_map = {
            "All": "전체",
            "Internal Medicine": "내과",
            "Orthopedics": "정형외과",
            "Pediatrics": "소아청소년과",
            "Dermatology": "피부과",
            "Ophthalmology": "안과",
            "ENT": "이비인후과",
            "Psychiatry": "정신건강의학과",
            "Obstetrics and Gynecology": "산부인과",
            "Dentistry": "치과",
            "Urology": "비뇨의학과",
            "Emergency Medicine": "응급의학과",
        }

        region = st.text_input("Enter a region (e.g., Seoul, Gyeonggi)", "")
        department_eng = st.selectbox("Medical Department", list(department_map.keys()))
        department_kor = department_map[department_eng]

        filtered = df.copy()
        if region:
            filtered = filtered[filtered["주소"].str.contains(region)]
        if department_kor != "전체":
            filtered = filtered[filtered["진료과목"].str.contains(department_kor)]

        st.markdown(f"🔍 {len(filtered)} hospitals found")

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
[View on Kakao Map](https://map.kakao.com/?q={row['병원명']})  
---""")
