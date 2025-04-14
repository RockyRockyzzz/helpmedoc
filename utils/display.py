import streamlit as st
import re

def display_medication_cards(gpt_text):
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
