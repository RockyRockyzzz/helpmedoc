# HelpMeDoc

An AI-powered Korean medical assistant chatbot designed for foreigners living in Korea.

Features:
- Symptom-based GPT chatbot
- OCR image upload and medication explanation
- Simple, Streamlit-powered interface

Deploy this app using Streamlit Cloud for quick web access.

GitHub: https://github.com/Rockyrockyzzz/helpmedoc


# 🦉 HelpMeDoc - Medical Chatbot MVP

**HelpMeDoc**는 한국의료 시스템에 익숙하지 않은 사용자(외국인, 노약자 등)를 위해 설계된 AI 기반 의료 챗봇 MVP입니다.  
증상 상담, 약품 인식, 병원 탐색까지 도와주는 의료 어시스턴트를 목표로 합니다.

---

## 🔧 구성 기능

### 🗣️ 챗봇 상담 (`chat.py`)
- 증상 기반 진료과 추천
- 응급 여부 판단 (triage)
- 사용자 입력 정보 반영 (나이, 성별 등)

### 📷 약품 OCR 분석 (`ocr.py`)
- 약 사진에서 이름 추출
- 식약처 기반 약 리스트와 유사도 비교
- GPT가 영어로 복약 정보 요약

### 🏥 병원 탐색 (`hospital.py`)
- 성남시 병원 CSV 기반
- 구 → 법정동 → 진료과 필터
- 카카오맵 링크 연동

### 🧪 프롬프트 자동 테스트 (`test_dori_prompts.py`)
- 다양한 증상 입력에 대해 챗봇 응답 품질 자동 테스트

---

## 🗂️ 프로젝트 구조

```
helpmedoc/
├── app.py                  # Streamlit 메인 앱
├── chat.py                 # 챗봇 상담 기능
├── ocr.py                  # OCR 및 약품 설명 기능
├── hospital.py             # 병원 검색 UI
├── display.py              # UI 구성 함수
├── test_dori_prompts.py    # 프롬프트 테스트 자동화
├── dori_prompt_test_script_input.json # 테스트 케이스
├── assets/
│   ├── dori.png                             # 도리 캐릭터 이미지
│   └── seongnam_hospital_with_departments.csv  # 병원 데이터
```

---

## ▶️ 실행 방법

```bash
pip install -r requirements_full.txt
streamlit run app.py
```

---

## 🙋‍♀ 기획자 메모

> 이 MVP는 **의료인(기획자)**과 **개발자(협업자)** 간의 협업을 전제로 구성되어 있습니다.  
향후 실 사용자 테스트, 모바일 최적화, 데이터 저장 기능 확장을 계획 중입니다.

---

## 📌 TODO (개발자 협업시 논의할 기능)

- [ ] 진료기록 저장 (csv/json)
- [ ] 챗봇-병원 자동 연동
- [ ] 사용자별 대화 요약 보기
- [ ] 모바일 UI 개선
- [ ] Streamlit Cloud 배포 자동화

---
