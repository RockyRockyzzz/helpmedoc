import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

@st.cache_data
def load_hospital_data():
    path = "hospital_sample.csv"
    if not os.path.exists(path):
        st.error("🚨 hospital_sample.csv 파일이 존재하지 않습니다.")
        return pd.DataFrame()
    return pd.read_csv(path)

def run_hospital_finder():
    df = load_hospital_data()
    if df.empty:
        st.warning("No hospital data found.")
        return

    department_map = {"All": "전체", "Internal Medicine": "내과", "Orthopedics": "정형외과", "Pediatrics": "소아청소년과", "Dermatology": "피부과", "Ophthalmology": "안과", "ENT": "이비인후과", "Psychiatry": "정신건강의학과", "Obstetrics and Gynecology": "산부인과", "Dentistry": "치과", "Urology": "비뇨의학과", "Emergency Medicine": "응급의학과"}
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
                tooltip=row["병원명"]
            ).add_to(m)
        st_folium(m, width=700, height=500)

        for _, row in filtered.iterrows():
            st.markdown(f"""**{row['병원명']}**  
{row['주소']}  
{row['전화번호']}  
[View on Kakao Map](https://map.kakao.com/?q={row['병원명']})  
---""")
