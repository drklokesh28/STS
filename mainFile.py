import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from streamlit_option_menu import option_menu
from pymongo import MongoClient

from Courses import main_layout as learn_layout
from Materials import main1 as study_materials
from Assignments import main2 as assignment_materials
from save_progress import main3 as save_progress
from Performance import main4 as performance_dashboard


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Learning Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# MONGODB CONNECTION
# ============================================================

@st.cache_resource(ttl=3600)
def init_connection():
    return MongoClient(
        st.secrets["DataBase"]["client"]
    )


def get_db():
    client = init_connection()
    return client["courses_db"]


# ============================================================
# SESSION STATE DEFAULT VALUES
# ============================================================

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


for key, default_value in SESSION_DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = default_value


# ============================================================
# DATABASE COLLECTION
# ============================================================

db = get_db()

st.session_state["collection"] = db["course_collection"]


# ============================================================
# ADVERTISEMENT
# ============================================================

def show_advertisement():

    ad_html = """
    <!DOCTYPE html>
    <html>

    <head>

        <style>

            html,
            body {
                margin: 0;
                padding: 0;
                background-color: transparent;
                overflow: hidden;
            }

            .ad-container {
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }

        </style>

    </head>

    <body>

        <div class="ad-container">

            <script type="text/javascript">

                atOptions = {
                    'key': '131d995d7da9099eed9bc1316ad6db41',
                    'format': 'iframe',
                    'height': 250,
                    'width': 300,
                    'params': {}
                };

            </script>

            <script
                type="text/javascript"
                src="https://www.highrevenueformat.com/131d995d7da9099eed9bc1316ad6db41/invoke.js">
            </script>

        </div>

    </body>

    </html>
    """

    components.html(
        ad_html,
        height=270,
        scrolling=False
    )


# ============================================================
# LOGIN DIALOG
# ============================================================

@st.dialog(
    "Enter Login Details",
    width="large"
)
def login():

    collection = st.session_state["collection"]

    # --------------------------------------------------------
    # INTRO VIDEO
    # --------------------------------------------------------

    st.video(
        "https://youtu.be/fGwPmCk64DA?si=55XzWIYApNWJjKQp",
        muted=True,
        autoplay=True
    )


    # --------------------------------------------------------
    # ADVERTISEMENT
    # --------------------------------------------------------

    show_advertisement()


    st.divider()


    # --------------------------------------------------------
    # ACADEMIC YEAR
    # --------------------------------------------------------

    st.subheader("📅 Select Academic Year")

    year = st.pills(
        "Academic Year",
        [
            "2025-2029",
            "2024-2028",
            "2023-2027"
        ],
        key="input_year"
    )


    # --------------------------------------------------------
    # DEPARTMENT
    # --------------------------------------------------------

    st.subheader("🏛️ Select Department")

    department = st.segmented_control(
        "Department",
        [
            "AI&DS",
            "DS",
            "AI",
            "CSE"
        ],
        key="input_dept"
    )


    # --------------------------------------------------------
    # LOAD SUBJECTS
    # --------------------------------------------------------

    if year and department:

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
            list(
                set(
                    document["courseName"]
                    for document in subjects_cursor
                    if "courseName" in document
                )
            )
        )


        # ----------------------------------------------------
        # SUBJECT SELECTION
        # ----------------------------------------------------

        if subjects:

            st.subheader("📚 Select Subject")

            subject = st.pills(
                "Subject",
                subjects,
                key="input_subject"
            )


            # ------------------------------------------------
            # GET STUDENTS
            # ------------------------------------------------

            if subject:

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


                if (
                    course_students
                    and "enrolledStudents" in course_students
                ):

                    enrolled = course_students["enrolledStudents"]


                    roll_options = [
                        student["student_roll_number"]
                        for student in enrolled
                        if "student_roll_number" in student
                    ]


                    if roll_options:

                        # ------------------------------------
                        # LOGIN FORM
                        # ------------------------------------

                        st.subheader(
                            "👤 Select Student & Password"
                        )


                        with st.form(
                            "login_form",
                            clear_on_submit=False
                        ):

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


                            # --------------------------------
                            # LOGIN VALIDATION
                            # --------------------------------

                            if submit_button:

                                if not password:

                                    st.warning(
                                        "⚠️ Please enter your password."
                                    )

                                else:

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


                                    # ------------------------
                                    # SUCCESS
                                    # ------------------------

                                    if course_data:

                                        student_info = next(
                                            (
                                                student
                                                for student
                                                in course_data.get(
                                                    "enrolledStudents",
                                                    []
                                                )
                                                if student.get(
                                                    "student_roll_number"
                                                ) == roll_number
                                            ),
                                            {}
                                        )


                                        st.session_state["logged_in"] = True

                                        st.session_state["year"] = year

                                        st.session_state[
                                            "department"
                                        ] = department

                                        st.session_state[
                                            "subject"
                                        ] = subject

                                        st.session_state[
                                            "roll_number"
                                        ] = roll_number

                                        st.session_state[
                                            "student_name"
                                        ] = student_info.get(
                                            "student_name",
                                            ""
                                        )

                                        st.session_state[
                                            "start_time"
                                        ] = datetime.now().strftime(
                                            "%H:%M:%S"
                                        )


                                        # --------------------
                                        # STORE COURSE DATA
                                        # --------------------

                                        for unit in [
                                            "unit 1",
                                            "unit 2",
                                            "unit 3",
                                            "unit 4",
                                            "unit 5",
                                            "materials"
                                        ]:

                                            st.session_state[
                                                unit
                                            ] = course_data.get(
                                                unit
                                            )


                                        st.session_state[
                                            "course_data"
                                        ] = course_data


                                        st.toast(
                                            "✅ Login Successful!"
                                        )


                                        st.rerun()


                                    # ------------------------
                                    # WRONG PASSWORD
                                    # ------------------------

                                    else:

                                        st.error(
                                            "❌ Invalid password."
                                        )


                    else:

                        st.warning(
                            "⚠️ No students are enrolled in this course."
                        )


                else:

                    st.warning(
                        "⚠️ No student information found for this subject."
                    )


        else:

            st.warning(
                "⚠️ No subjects available for the selected "
                "academic year and department."
            )


# ============================================================
# LOGOUT
# ============================================================

def logout():

    collection = st.session_state.get("collection")


    # Remove everything
    st.session_state.clear()


    # Restore collection
    if collection is not None:
        st.session_state["collection"] = collection


    # Restore defaults
    for key, default_value in SESSION_DEFAULTS.items():

        if key not in st.session_state:
            st.session_state[key] = default_value


    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

def show_sidebar():

    with st.sidebar:

        # ----------------------------------------------------
        # STUDENT INFORMATION
        # ----------------------------------------------------

        if st.session_state.get(
            "logged_in",
            False
        ):

            st.write(
                f"👋 **Welcome, "
                f"{st.session_state.get('student_name', 'Student')}**"
            )

            st.caption(
                f"Roll No: "
                f"{st.session_state.get('roll_number')} "
                f"| "
                f"{st.session_state.get('department')}"
            )

            st.caption(
                f"📚 "
                f"{st.session_state.get('subject', '')}"
            )

            st.divider()


        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.session_state.get(
            "logged_in",
            False
        ):

            st.divider()

            st.button(
                "🚪 Logout",
                on_click=logout,
                use_container_width=True
            )


        return selected


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # --------------------------------------------------------
    # NOT LOGGED IN
    # --------------------------------------------------------

    if not st.session_state.get(
        "logged_in",
        False
    ):

        login()

        return


    # --------------------------------------------------------
    # LOGGED IN
    # --------------------------------------------------------

    selected = show_sidebar()


    # --------------------------------------------------------
    # LEARN
    # --------------------------------------------------------

    if selected == "Learn":

        learn_layout()


    # --------------------------------------------------------
    # STUDY
    # --------------------------------------------------------

    elif selected == "Study":

        study_materials()


    # --------------------------------------------------------
    # ASSIGNMENT
    # --------------------------------------------------------

    elif selected == "Assignment":

        assignment_materials()


    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    elif selected == "My Performance":

        performance_dashboard()


    # --------------------------------------------------------
    # SAVE PROGRESS
    # --------------------------------------------------------

    elif selected == "Save My Progress":

        save_progress()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    main()
