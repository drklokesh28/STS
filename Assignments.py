import streamlit as st
from datetime import datetime
import pandas as pd

def main_layout():
    st.subheader("📝 My Assignments", divider="orange", text_alignment="center")
    
    if not st.session_state.get("roll_number"):
        st.warning("⚠️ Please log in to view assignments")
        return

    col1, col2 = st.columns([1, 2], border=True, gap="small")
    
    with col1:
        st.subheader("🔍 Select Assignment", divider="blue")
        course_data = st.session_state.get("course_data")
        
        if not course_data or "tasks" not in course_data or not course_data["tasks"]:
            st.info("ℹ️ No assignments available")
            return

        task_dates = sorted(list({task["task_date"] for task in course_data["tasks"]}))
        
        if task_dates:
            selected_date = st.date_input("Select Assignment Date", value=datetime.strptime(task_dates[0], "%Y-%m-%d").date())
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            
            tasks_for_date = [t for t in course_data["tasks"] if t["task_date"] == selected_date_str]
            if tasks_for_date:
                selected_task_name = st.selectbox("Select Assignment", [t["task_name"] for t in tasks_for_date])
                selected_task = next((t for t in tasks_for_date if t["task_name"] == selected_task_name), None)
                
                if selected_task:
                    student_roll = st.session_state["roll_number"]
                    student_stats = next((s for s in selected_task.get("stats", []) if s.get("student_roll_number") == student_roll), None)
                    
                    if student_stats and student_stats.get("status") == "completed":
                        st.success("✅ Already Completed!")
                        st.write(f"**Marks Obtained:** {student_stats.get('total_marks_obtained', 0)}/{selected_task.get('total_marks', 0)}")
                    else:
                        st.warning("⏳ Not Completed")
                        if st.button("📝 Attempt Test", use_container_width=True):
                            st.session_state["attempting_task"] = {"task_date": selected_date_str, "task_name": selected_task_name}
                            st.session_state["show_assignment"] = True
                            st.session_state["assignment_answers"] = {}
                            st.session_state["assignment_start_time"] = None
                            st.rerun()

    with col2:
        if st.session_state.get("show_assignment") and "attempting_task" in st.session_state:
            attempt_data = st.session_state["attempting_task"]
            task = next((t for t in st.session_state.get("course_data", {}).get("tasks", []) 
                        if t["task_date"] == attempt_data["task_date"] and t["task_name"] == attempt_data["task_name"]), None)
            
            if task:
                st.subheader(f"📝 {task['task_name']}", divider="blue")
                questions = task.get("questions", [])
                
                for idx, q in enumerate(questions):
                    opts = [q.get("option a"), q.get("option b"), q.get("option c"), q.get("option d")]
                    opts = [o for o in opts if o]
                    st.write(f"**Q{idx+1}.** {q.get('question name', '')}")
                    
                    select_key = f"q_{idx}_{task['task_date']}_{task['task_name']}"
                    ans = st.selectbox("Answer", ["Select an option..."] + opts, key=select_key)
                    if ans != "Select an option...":
                        st.session_state["assignment_answers"][select_key] = ans
                    st.divider()

                if st.button("📤 Submit Assignment", type="primary", use_container_width=True):
                    if len(st.session_state["assignment_answers"]) < len(questions):
                        st.error("⚠️ Answer all questions before submitting.")
                    else:
                        marks = sum(1 for idx, q in enumerate(questions) 
                                    if st.session_state["assignment_answers"].get(f"q_{idx}_{task['task_date']}_{task['task_name']}") == q.get("correct answer"))
                        st.session_state["assignment_marks"] = marks
                        st.session_state["submit_assignment"] = True
                        st.session_state["show_assignment"] = False
                        st.rerun()

        elif st.session_state.get("submit_assignment"):
            marks = st.session_state.get("assignment_marks", 0)
            st.subheader("📊 Assignment Results", divider="orange")
            st.write(f"**✅ Marks Obtained:** {marks}")
            
            if st.button("✅ Save Results", type="primary", use_container_width=True):
                if update_assignment_results(marks):
                    st.session_state["submit_assignment"] = False
                    st.rerun()

def update_assignment_results(marks_obtained):
    try:
        collection = st.session_state.get("collection")
        attempt_data = st.session_state.get("attempting_task")
        student_roll = st.session_state.get("roll_number")
        
        result = collection.update_one(
            {
                "academicYear": st.session_state["year"],
                "department": st.session_state["department"],
                "courseName": st.session_state["subject"],
                "tasks.task_date": attempt_data["task_date"],
                "tasks.task_name": attempt_data["task_name"],
                "tasks.stats.student_roll_number": student_roll
            },
            {
                "$set": {
                    "tasks.$[t].stats.$[s].status": "completed",
                    "tasks.$[t].stats.$[s].total_marks_obtained": marks_obtained,
                    "tasks.$[t].stats.$[s].completed_date": datetime.now().strftime("%Y-%m-%d")
                }
            },
            array_filters=[
                {"t.task_date": attempt_data["task_date"], "t.task_name": attempt_data["task_name"]},
                {"s.student_roll_number": student_roll}
            ]
        )
        return result.modified_count > 0
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

def main2():
    main_layout()
