import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

def main_layout():
    st.subheader("📊 My Performance Dashboard", divider="orange", text_alignment="center")
    
    if not st.session_state.get("roll_number"):
        st.warning("⚠️ Please log in to view performance data")
        return

    student_data = fetch_student_data()
    if not student_data:
        st.info("ℹ️ No performance data available yet.")
        return

    track_data = student_data.get("track", [])
    daily_records = []
    
    for entry in track_data:
        date_str = entry.get("date", "")
        sessions = entry.get("study_time", [])
        total_seconds = 0
        for s in sessions:
            try:
                parts = s.split(" - ")
                t1 = datetime.strptime(parts[0].strip(), "%H:%M:%S")
                t2 = datetime.strptime(parts[1].strip(), "%H:%M:%S")
                diff = (t2 - t1).total_seconds()
                total_seconds += diff if diff > 0 else (diff + 86400)
            except:
                pass
        
        if total_seconds > 0:
            daily_records.append({"Date": date_str, "Study Seconds": total_seconds, "Sessions": len(sessions)})

    if daily_records:
        df = pd.DataFrame(daily_records)
        st.metric("Total Sessions", df["Sessions"].sum())
        st.metric("Total Study Hours", round(df["Study Seconds"].sum() / 3600, 2))
        
        fig = px.bar(df, x="Date", y="Study Seconds", title="Daily Study Time")
        st.plotly_chart(fig, use_container_width=True)

def fetch_student_data():
    collection = st.session_state.get("collection")
    if collection is None:
        return None
    
    course_data = collection.find_one({
        "academicYear": st.session_state.get("year"),
        "department": st.session_state.get("department"),
        "courseName": st.session_state.get("subject"),
        "enrolledStudents.student_roll_number": st.session_state.get("roll_number")
    }, {"enrolledStudents.$": 1})
    
    if course_data and "enrolledStudents" in course_data:
        return course_data["enrolledStudents"][0]
    return None

def main4():
    main_layout()
