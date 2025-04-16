
import streamlit as st
import pandas as pd

@st.cache_data
def load_hospital_data():
    df = pd.read_csv("assets/seongnam_hospital_with_departments.csv", encoding="utf-8-sig")
    return df

# 법정동 기준으로 구 분류
법정동_구_맵 = {
    "정자동": "분당구", "서현동": "분당구", "이매동": "분당구", "야탑동": "분당구",
    "백현동": "분당구", "삼평동": "분당구", "판교동": "분당구", "수내동": "분당구", "금곡동": "분당구",
    "수진동": "수정구", "신흥동": "수정구", "단대동": "수정구", "산성동": "수정구",
    "양지동": "수정구", "복정동": "수정구", "위례동": "수정구", "신촌동": "수정구",
    "중앙동": "중원구", "성남동": "중원구", "하대원동": "중원구", "상대원동": "중원구",
    "금광동": "중원구", "은행동": "중원구"
}

def run_hospital_finder():
    st.subheader("🏥 성남시 병원 탐색")
    df = load_hospital_data()

    # '구' 추가
    df["구"] = df["법정동"].map(법정동_구_맵).fillna("기타")

    # 구 선택
    구목록 = ["전체"] + sorted(df["구"].unique().tolist())
    선택구 = st.selectbox("📍 구 선택", 구목록)
    if 선택구 != "전체":
        df = df[df["구"] == 선택구]

    # 법정동 선택
    동목록 = ["전체"] + sorted(df["법정동"].dropna().unique().tolist())
    선택동 = st.selectbox("🧭 법정동 선택", 동목록)
    if 선택동 != "전체":
        df = df[df["법정동"] == 선택동]

    # 진료과 선택
    진료과목목록 = ["전체"] + sorted(df["진료과"].dropna().unique().tolist())
    선택진료과 = st.selectbox("🩺 진료과 선택", 진료과목목록)
    if 선택진료과 != "전체":
        df = df[df["진료과"] == 선택진료과]

    st.markdown(f"### 🔎 검색 결과: {len(df)}개 병원")

    for _, row in df.iterrows():
        st.markdown(f"""
**{row['의료기관명']}**  
📍 {row['의료기관주소(도로명)']}  
📞 {row['의료기관전화번호']}  
[카카오맵에서 보기](https://map.kakao.com/?q={row['의료기관명']})  
---
""")
