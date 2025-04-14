import streamlit as st

def run_chat_interface(client):
    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input("Ask Dori about symptoms, clinics, or emergencies...", label_visibility="collapsed", key="user_input")
    with col2:
        submitted = st.button("↑", use_container_width=True)

    if submitted and user_input:
        messages = [
            {"role": "system", "content": "You are a friendly and knowledgeable medical assistant helping foreigners..."},
            {"role": "user", "content": user_input}
        ]
        with st.spinner("Dori is thinking..."):
            try:
                response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"GPT Error: {e}")
