import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="HelpMeDoc", layout="wide")

st.title("🦉 HelpMeDoc – Medical Assistant for Foreigners in Korea")

# 사이드바 메뉴
menu = st.sidebar.radio("기능을 선택하세요", ["💬 Dori와 대화", "💊 약 이미지 해석", "🏥 병원 탐색"])
st.sidebar.markdown("✅ 사이드바 정상 작동 중")

# 병원 CSV 로드
@st.cache_data
def load_hospital_data():
    path = "hospital_sample.csv"
    if not os.path.exists(path):
        st.error("🚨 병원 데이터 파일(hospital_sample.csv)을 찾을 수 없습니다.")
        return pd.DataFrame()
    return pd.read_csv(path)

# 병원 탐색 탭
if menu == "🏥 병원 탐색":
    df = load_hospital_data()

    if df.empty:
        st.warning("불러올 수 있는 병원 데이터가 없습니다. hospital_sample.csv 파일을 확인해주세요.")
    else:
        st.subheader("🏥 병원 탐색")
        region = st.text_input("지역을 입력하세요 (예: 서울, 경기, 부산)", "")
        department = st.selectbox("진료과목을 선택하세요", ["전체", "내과", "정형외과"])

        filtered = df.copy()
        if region:
            filtered = filtered[filtered["주소"].str.contains(region)]
        if department != "전체":
            filtered = filtered[filtered["진료과목"] == department]

        st.markdown(f"🔍 총 {len(filtered)}개 병원 검색됨")

        # 지도 마커 표시
        if not filtered.empty:
            avg_lat = filtered["위도"].mean()
            avg_lon = filtered["경도"].mean()
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
            for _, row in filtered.iterrows():
                folium.Marker(
                    location=[row["위도"], row["경도"]],
                    popup=f"{row['병원명']}<br>{row['주소']}",
                    tooltip=row["병원명"],
                ).add_to(m)
            st_folium(m, width=700, height=500)

        # 병원 리스트
        for _, row in filtered.iterrows():
            st.markdown(f"""**{row['병원명']}**  
{row['주소']}  
{row['전화번호']}  
[카카오맵으로 보기](https://map.kakao.com/?q={row['병원명']})  
---""")