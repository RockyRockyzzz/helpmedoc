import streamlit as st

def run_chat_interface(client):
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

    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input("Ask Dori about symptoms, clinics, or emergencies...", label_visibility="collapsed", key="user_input")
    with col2:
        submitted = st.button("↑", use_container_width=True)

    if submitted and user_input:
        messages = [
            {"role": "system", "content": """You are a friendly and knowledgeable medical assistant helping foreigners living in Korea.
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
"""},
            {"role": "user", "content": user_input}
        ]
        with st.spinner("Dori is thinking..."):
            try:
                response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                dori_reply = response.choices[0].message.content

                col1, col2 = st.columns([1, 9])
                with col1:
                    st.image("dori_2D.png", width=50)
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
                    {dori_reply}
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"GPT Error: {e}")
