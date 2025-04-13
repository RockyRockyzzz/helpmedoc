import streamlit as st

st.set_page_config(page_title="Chat with Dori", layout="centered")

st.title("🦉 Chat with Dori – Medical Assistant")

# Sample user and Dori interaction
st.markdown("### Conversation Example")

user_msg = "I have a headache. What should I do?"
dori_msg = "You should visit 내과 (Internal Medicine). Here's a <a href='https://map.kakao.com/?q=내과' target='_blank'>map link</a>."

# User bubble
user_col1, user_col2 = st.columns([9, 1])
with user_col1:
    st.markdown(
        f'''
<div style="background-color: #dbeafe; padding: 10px 15px; border-radius: 12px; display: inline-block; margin-bottom: 10px;">
    <b>You:</b> {user_msg}
</div>
        ''',
        unsafe_allow_html=True
    )
with user_col2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Sample_User_Icon.png/240px-Sample_User_Icon.png", width=40)

# Dori bubble
dori_col1, dori_col2 = st.columns([1, 9])
with dori_col1:
    st.image("dori_2d_cartoon.png", width=40)
with dori_col2:
    st.markdown(
        f'''
<div style="background-color: #f1f3f5; padding: 10px 15px; border-radius: 12px; display: inline-block;">
    <b>Dori:</b> {dori_msg}
</div>
        ''',
        unsafe_allow_html=True
    )