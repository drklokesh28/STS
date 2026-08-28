import streamlit as st
from advertisements import *

def main_layout():
    st.subheader("YOU CURRENTLY DECIDED TO LEARN", divider="orange", text_alignment="center")
    col1, col2 = st.columns([1, 2], border=True, gap="small")
    
    options = col1.radio("Select The Unit To Learn", ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"], horizontal=True)
    with col1:
        show_advertisement()
    
    unit_key = options.lower()
    unit_data = st.session_state.get(unit_key, [])
    
    if not unit_data:
        col2.info("No content available for this unit.")
        return

    topic_names = [t["topic_name"] for t in unit_data if "topic_name" in t]
    select_topic = col2.selectbox("Select the topic that you wanted to learn", topic_names)

    selected_data = next((t for t in unit_data if t.get("topic_name") == select_topic), None)
    
    if selected_data:
        col2.video(selected_data.get("yt_link", ""))
        col2.text(selected_data.get("description", ""))
        with col2:
            show_advertisement()
