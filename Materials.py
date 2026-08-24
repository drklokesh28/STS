import streamlit as st
import os
from streamlit_pdf_viewer import pdf_viewer

@st.cache_data(ttl=3600, show_spinner=False)
def read_local_pdf_bytes(file_path: str) -> bytes:
    """
    Fast-reads local PDF bytes and caches them in memory.
    Prevents repeated disk reading delays during app reruns or tab switches.
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
    return None


def main_layout():
    """
    Main layout for the Study/Materials section.
    Displays local PDF materials organized by category using st.session_state['materials'].
    """
    st.subheader("📚 Study Materials", divider="orange", text_alignment="center")
    
    # Read materials stored in session state
    materials_data = st.session_state.get("materials")
    if not materials_data:
        st.info("ℹ️ No materials available for this course")
        return
    
    # Extract unique categories from session state
    categories = sorted(list(set([material["category"].strip() for material in materials_data if material.get("category")])))
    
    if not categories:
        st.info("ℹ️ No categories found in materials")
        return
    
    # Create two columns with 1:2 ratio
    col1, col2 = st.columns([1, 2], border=True, gap="small")
    
    # Column 1: Display categories as pills
    with col1:
        st.subheader("📁 Categories", divider="blue")
        selected_category = st.pills(
            "Select Category",
            options=categories,
            selection_mode="single",
            key="materials_category_pills"
        )
    
    # Column 2: Display materials based on selected category
    with col2:
        if selected_category:
            # Filter materials by selected category
            category_materials = [
                m for m in materials_data 
                if m.get("category", "").strip() == selected_category
            ]
            
            if category_materials:
                st.subheader(f"📄 {selected_category} Materials", divider="blue")
                
                material_options = []
                material_map = {}
                
                for material in category_materials:
                    materials_list = [m.strip() for m in material.get("materials", "").split(",") if m.strip()]
                    root_path = material.get("root_path", "").strip()
                    
                    for material_name in materials_list:
                        # Construct and normalize disk path cleanly
                        full_path = os.path.normpath(os.path.join(root_path, material_name))
                        
                        material_map[material_name] = {
                            "root_path": root_path,
                            "material_name": material_name,
                            "full_path": full_path
                        }
                        material_options.append(material_name)
                
                if material_options:
                    selected_material = st.selectbox(
                        "Select Material to View",
                        options=material_options,
                        key="materials_selectbox"
                    )
                    
                    if selected_material and selected_material in material_map:
                        material_info = material_map[selected_material]
                        full_path = material_info["full_path"]
                        
                        # Display path info
                        st.caption(f"📂 **Path:** `{full_path}`")
                        
                        # Check if local file exists
                        if os.path.exists(full_path):
                            # Load PDF via fast memory cache
                            pdf_bytes = read_local_pdf_bytes(full_path)
                            
                            if pdf_bytes:
                                st.info("📄 PDF Viewer")
                                
                                # Fast render PDF
                                pdf_viewer(
                                    input=pdf_bytes,
                                    key=f"pdf_viewer_{hash(selected_material)}"
                                )
                                
                                # Download PDF Button
                                st.download_button(
                                    label="📥 Download PDF",
                                    data=pdf_bytes,
                                    file_name=selected_material,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            else:
                                st.error("❌ Could not read PDF bytes from specified path.")
                        else:
                            st.error(f"❌ File not found at: `{full_path}`")
                            st.info("💡 Tip: Verify that the local folder and PDF file name match your database record exactly.")
                else:
                    st.info("ℹ️ No materials found in this category")
            else:
                st.info("ℹ️ No materials found for the selected category")
        else:
            st.info("👈 Please select a category from the left to view materials")


def main1():
    """
    Wrapper function for the materials section
    Called from mainFile.py when 'Study' is selected
    """
    main_layout()
