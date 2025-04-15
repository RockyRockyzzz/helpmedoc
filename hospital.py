
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse
import json

department_code_map = {"내과": "01", "정형외과": "02", "소아청소년과": "03", "피부과": "04", "안과": "05", "이비인후과": "06", "정신건강의학과": "07", "산부인과": "08", "치과": "49", "비뇨의학과": "09", "응급의학과": "10"}
sido_sggu_map = {
    "서울특별시": {
        "code": "110000",
        "districts": {
            "강남구": "110019",
            "강동구": "110020",
            "강북구": "110021",
            "강서구": "110022"
        }
    },
    "경기도": {
        "code": "410000",
        "districts": {
            "수원시 장안구": "411111",
            "수원시 권선구": "411113",
            "수원시 팔달구": "411115",
            "수원시 영통구": "411117"
        }
    }
}

@st.cache_data
def fetch_hospitals(dgsbjt_code, sido_code, sggu_code=None, num_rows=20):
    service_key = "O0wI7BmTCPHgoS8Trmp9INLhy1qVqdWR/wUaKnlnTDeY/ZNsc4wrkOqolStMSZoHjdjJ8GEoL1MxqmGyMc6vxA=="
    encoded_key = urllib.parse.quote(service_key, safe='')

    base_url = "https://apis.data.go.kr/B551182/hospInfoService2/getHospBasisList"
    query = f"?serviceKey={encoded_key}&sidoCd={sido_code}&dgsbjtCd={dgsbjt_code}&pageNo=1&numOfRows={num_rows}"
    if sggu_code:
        query += f"&sgguCd={sggu_code}"
    url = base_url + query

    try:
        res = requests.get(url, timeout=5,verify=False)
        res.raise_for_status()
        root = ET.fromstring(res.text)
        hospitals = []
        for item in root.iter("item"):
            name = item.findtext("yadmNm", default="").strip()
            addr = item.findtext("addr", default="").strip()
            tel = item.findtext("telno", default="").strip()
            hospitals.append({"병원명": name, "주소": addr, "전화번호": tel})
        return hospitals
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

def run_hospital_finder():
    st.subheader("🏥 병원 탐색 (URL 조립 방식)")
    department = st.selectbox("진료과 선택", list(department_code_map.keys()))
    region = st.selectbox("시/도 선택", list(sido_sggu_map.keys()))
    sub_region = st.selectbox("시/군/구 선택", list(sido_sggu_map[region]["districts"].keys()))

    if st.button("🔍 병원 검색"):
        dgsbjt_code = department_code_map[department]
        sido_code = sido_sggu_map[region]["code"]
        sggu_code = sido_sggu_map[region]["districts"][sub_region]
        hospitals = fetch_hospitals(dgsbjt_code, sido_code, sggu_code)
        st.markdown(f"### 🔎 {{len(hospitals)}}개 병원 검색됨")

        for hosp in hospitals:
            st.markdown(f"""
**{{hosp['병원명']}}**  
📍 {{hosp['주소']}}  
📞 {{hosp['전화번호']}}  
[카카오맵에서 보기](https://map.kakao.com/?q={{urllib.parse.quote(hosp['병원명'])}})  
---
""")