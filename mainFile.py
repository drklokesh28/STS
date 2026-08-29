import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_option_menu import option_menu
from pymongo import MongoClient

from Courses import main_layout as learn_layout
from Materials import main1 as study_materials
from Assignments import main2 as assignment_materials
from save_progress import main3 as save_progress
from Performance import main4 as performance_dashboard
import advertisements as ads

st.set_page_config(
    page_title="Student Learning Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource(ttl=3600)
def init_connection():
    return MongoClient(st.secrets["DataBase"]["client"])

def get_db():
    return init_connection()["courses_db"]

SESSION_DEFAULTS = {
    "logged_in": False,
    "unit 1": None,
    "unit 2": None,
    "unit 3": None,
    "unit 4": None,
    "unit 5": None,
    "materials": None,
    "start_time": None,
    "year": None,
    "department": None,
    "subject": None,
    "roll_number": None,
    "student_name": None,
    "course_data": None,
    "attempting_task": None,
    "assignment_answers": {},
    "assignment_marks": 0,
    "submit_assignment": False,
    "assignment_start_time": None,
    "show_assignment": None,
    "progress_saved": False
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

db = get_db()
st.session_state["collection"] = db["course_collection"]

@st.dialog("Enter Login Details", width="large")
def login():
    collection = st.session_state["collection"]

    st.video(
        "https://youtu.be/fGwPmCk64DA?si=55XzWIYApNWJjKQp",
        muted=True,
        autoplay=True
    )

    st.divider()

    st.subheader("📅 Select Academic Year")

    year = st.pills(
        "Academic Year",
        ["2025-2029", "2024-2028", "2023-2027"],
        key="input_year"
    )

    st.subheader("🏛️ Select Department")

    department = st.segmented_control(
        "Department",
        ["AI&DS", "DS", "AI", "CSE"],
        key="input_dept"
    )

    if not year or not department:
        return

    subjects_cursor = collection.find(
        {
            "academicYear": year,
            "department": department
        },
        {
            "_id": 0,
            "courseName": 1
        }
    )

    subjects = sorted(
        {
            document["courseName"]
            for document in subjects_cursor
            if document.get("courseName")
        }
    )

    if not subjects:
        st.warning("⚠️ No subjects available for the selected academic year and department.")
        return

    st.subheader("📚 Select Subject")

    subject = st.pills(
        "Subject",
        subjects,
        key="input_subject"
    )

    if not subject:
        return

    course_students = collection.find_one(
        {
            "academicYear": year,
            "department": department,
            "courseName": subject
        },
        {
            "_id": 0,
            "enrolledStudents.student_roll_number": 1,
            "enrolledStudents.student_name": 1
        }
    )

    if not course_students or "enrolledStudents" not in course_students:
        st.warning("⚠️ No student information found for this subject.")
        return

    enrolled = course_students.get("enrolledStudents", [])

    roll_options = [
        student.get("student_roll_number")
        for student in enrolled
        if student.get("student_roll_number")
    ]

    if not roll_options:
        st.warning("⚠️ No students are enrolled in this course.")
        return

    st.subheader("👤 Select Student & Password")

    with st.form("login_form", clear_on_submit=False):
        roll_number = st.selectbox(
            "Roll Number",
            roll_options
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submit_button = st.form_submit_button(
            "🔓 Log In",
            use_container_width=True
        )

    if not submit_button:
        return

    if not password:
        st.warning("⚠️ Please enter your password.")
        return

    course_data = collection.find_one(
        {
            "academicYear": year,
            "department": department,
            "courseName": subject,
            "enrolledStudents": {
                "$elemMatch": {
                    "student_roll_number": roll_number,
                    "student_password": password
                }
            }
        }
    )

    if not course_data:
        st.error("❌ Invalid password.")
        return

    student_info = next(
        (
            student
            for student in course_data.get("enrolledStudents", [])
            if student.get("student_roll_number") == roll_number
        ),
        {}
    )

    st.session_state["logged_in"] = True
    st.session_state["year"] = year
    st.session_state["department"] = department
    st.session_state["subject"] = subject
    st.session_state["roll_number"] = roll_number
    st.session_state["student_name"] = student_info.get("student_name", "")

    st.session_state["start_time"] = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%I:%M:%S %p")

    for unit in [
        "unit 1",
        "unit 2",
        "unit 3",
        "unit 4",
        "unit 5",
        "materials"
    ]:
        st.session_state[unit] = course_data.get(unit)

    st.session_state["course_data"] = course_data

    st.toast("✅ Login Successful!")
    st.rerun()

def logout():
    collection = st.session_state.get("collection")

    st.session_state.clear()

    if collection is not None:
        st.session_state["collection"] = collection

    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.rerun()

def show_sidebar():
    with st.sidebar:
        st.write(
            f"👋 **Welcome, {st.session_state.get('student_name', 'Student')}**"
        )

        st.caption(
            f"Roll No: {st.session_state.get('roll_number', '')} | "
            f"{st.session_state.get('department', '')}"
        )

        st.caption(
            f"📚 {st.session_state.get('subject', '')}"
        )

        st.caption(
            f"🕐 Login Time: {st.session_state.get('start_time', '')}"
        )

        st.divider()

        selected = option_menu(
            menu_title="Main Menu",
            options=[
                "Learn",
                "Study",
                "Assignment",
                "My Performance",
                "Save My Progress"
            ],
            icons=[
                "book",
                "pencil-square",
                "clipboard-check",
                "person-circle",
                "save"
            ],
            menu_icon="star",
            default_index=0
        )

        ads.show_advertisement()
        ads.show_advertisement1()
        ads.show_advertisement2()

        ads.show_advertisement()
        ads.show_advertisement1()
        ads.show_advertisement2()

        ads.show_advertisement()
        ads.show_advertisement1()
        ads.show_advertisement2()

        ads.show_advertisement()
        ads.show_advertisement1()
        ads.show_advertisement2()

        st.divider()

        st.button(
            "🚪 Logout",
            on_click=logout,
            use_container_width=True
        )

        return selected

def main():
    if not st.session_state.get("logged_in", False):
        login()
        return

    selected = show_sidebar()

    if selected == "Learn":
        learn_layout()

    elif selected == "Study":
        study_materials()

    elif selected == "Assignment":
        assignment_materials()

    elif selected == "My Performance":
        performance_dashboard()

    elif selected == "Save My Progress":
        save_progress()

if __name__ == "__main__":
    main()
