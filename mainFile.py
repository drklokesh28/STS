import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu
from pymongo import MongoClient

# Import main layouts from external modules
from Courses import main_layout
from Materials import main1 as study_materials
from Assignments import main2 as assignment_materials
from save_progress import main3 as save_progress
from Performance import main4 as performance_dashboard

# --- DATABASE CONNECTION CACHING ---
@st.cache_resource
def init_connection():
    """Cache MongoDB connection to prevent reconnecting on every rerun."""
    return MongoClient(st.secrets["DataBase"]["client"])

if "client" not in st.session_state:
    st.session_state["client"] = init_connection()
    st.session_state["db"] = st.session_state["client"]["courses_db"]
    st.session_state["collection"] = st.session_state["db"]["course_collection"]

# --- SESSION STATE INITIALIZATION ---
SESSION_DEFAULTS = {
    "logged_in": False,
    "unit 1": None, "unit 2": None, "unit 3": None, "unit 4": None, "unit 5": None,
    "materials": None, "start_time": None, "year": None, "department": None,
    "subject": None, "roll_number": None, "student_name": None, "course_data": None,
    "attempting_task": None, "assignment_answers": {}, "assignment_marks": 0,
    "submit_assignment": False, "assignment_start_time": None, "show_assignment": None,
    "progress_saved": False
}

for key, default_val in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


# --- FAST & OPTIMIZED LOGIN DIALOG ---
@st.dialog("Enter Login Details")
def login():
    st.video("https://youtu.be/fGwPmCk64DA?si=55XzWIYApNWJjKQp", muted=True, autoplay=True)
    
    collection = st.session_state["collection"]
    if collection is None:
        st.error("❌ Database connection failed.")
        return

    st.subheader("📅 Select Academic Year")
    year = st.pills("Academic Year", ["2025-2029", "2024-2028", "2023-2027"], key="input_year")
    
    st.subheader("🏛️ Select Department")
    department = st.segmented_control("Department", ["AI&DS", "DS", "AI", "CSE"], key="input_dept")

    if year and department:
        # Optimized database query to fetch matching subjects only
        subjects_cursor = collection.find(
            {"academicYear": year, "department": department},
            {"_id": 0, "courseName": 1}
        )
        subjects = list(set(x["courseName"] for x in subjects_cursor if "courseName" in x))
        
        if subjects:
            st.subheader("📚 Select Subject")
            subject = st.pills("Subject", subjects, key="input_subject")
            
            if subject:
                # Fetch enrolled student roll numbers for the selected course
                course_students = collection.find_one(
                    {"academicYear": year, "department": department, "courseName": subject},
                    {"_id": 0, "enrolledStudents.student_roll_number": 1, "enrolledStudents.student_name": 1}
                )
                
                if course_students and "enrolledStudents" in course_students:
                    enrolled = course_students["enrolledStudents"]
                    roll_options = [s["student_roll_number"] for s in enrolled]
                    
                    st.subheader("👤 Select Student & Password")
                    
                    # Use a form to prevent expensive database lookups on every keystroke
                    with st.form("login_form", clear_on_submit=False):
                        roll_number = st.selectbox("Roll Number", roll_options)
                        password = st.text_input("Password", type="password")
                        submit_button = st.form_submit_button("🔓 Log In", use_container_width=True)
                        
                        if submit_button:
                            if not password:
                                st.warning("⚠️ Please enter your password.")
                            else:
                                # Fetch course document matching user parameters & credentials
                                course_data = collection.find_one({
                                    "academicYear": year,
                                    "department": department,
                                    "courseName": subject,
                                    "enrolledStudents": {
                                        "$elemMatch": {
                                            "student_roll_number": roll_number,
                                            "student_password": password
                                        }
                                    }
                                })
                                
                                if course_data:
                                    # Identify student name
                                    student_info = next(
                                        (s for s in course_data.get("enrolledStudents", []) if s.get("student_roll_number") == roll_number), 
                                        {}
                                    )
                                    
                                    # Populate Session States
                                    st.session_state["logged_in"] = True
                                    st.session_state["year"] = year
                                    st.session_state["department"] = department
                                    st.session_state["subject"] = subject
                                    st.session_state["roll_number"] = roll_number
                                    st.session_state["student_name"] = student_info.get("student_name", "")
                                    st.session_state["start_time"] = datetime.now().strftime("%H:%M:%S")
                                    
                                    # Load Unit & Course Data
                                    for unit in ["unit 1", "unit 2", "unit 3", "unit 4", "unit 5", "materials"]:
                                        st.session_state[unit] = course_data.get(unit)
                                    st.session_state["course_data"] = course_data

                                    st.toast("✅ Login Successful!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid password. Please try again.")
                else:
                    st.info("ℹ️ No students enrolled in this course.")
        else:
            st.info("ℹ️ No subjects present for selected Year & Department.")


# --- SIDEBAR & NAVIGATION ---
def show_sidebar():
    """Display navigation options in the sidebar."""
    with st.sidebar:
        if st.session_state.get("logged_in", False):
            st.write(f"👋 **Welcome, {st.session_state.get('student_name', 'Student')}**")
            st.caption(f"Roll No: {st.session_state.get('roll_number')} | {st.session_state.get('department')}")
            st.divider()
            
        selected = option_menu(
            "Main Menu",
            options=["Learn", "Study", "Assignment", "My Performance", "Save My Progress"],
            icons=["book", "pencil-square", "clipboard-check", "person-circle", "save"],
            menu_icon="star",
            default_index=0
        )
        
        if st.session_state.get("logged_in", False):
            st.sidebar.button("🚪 Logout", on_click=logout, use_container_width=True)
            
        return selected


def logout():
    """Clear user-specific session state on logout."""
    keep_keys = ["client", "db", "collection"]
    for key in list(st.session_state.keys()):
        if key not in keep_keys:
            del st.session_state[key]
    st.rerun()


def display_performance_dashboard():
    """Safely invoke performance dashboard module."""
    try:
        performance_dashboard()
    except Exception as e:
        st.error(f"❌ Error loading performance dashboard: {str(e)}")


# --- MAIN APPLICATION ENTRY POINT ---
def main():
    st.set_page_config(
        page_title="Student Learning Platform",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        .stApp { background-color: #f8f9fa; }
        .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stButton button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get("logged_in", False):
        login()
    else:
        selected = show_sidebar()
        
        if selected == "Learn":
            main_layout()
        elif selected == "Study":
            study_materials()
        elif selected == "Assignment":
            assignment_materials()
        elif selected == "My Performance":
            display_performance_dashboard()
        elif selected == "Save My Progress":
            save_progress()

if __name__ == "__main__":
    main()
