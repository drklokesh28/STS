import streamlit as st
import os

def main_layout():
    """
    Main layout for the Study/Materials section.
    Displays local PDF materials organized by category directly using st.pdf.
    """
    st.subheader("📚 Study Materials", divider="orange", text_alignment="center")
    
    # Read materials stored in session state
    materials_data = st.session_state.get("materials")
    if not materials_data:
        st.info("ℹ️ No materials available for this course")
        return
    
    # Extract unique categories cleanly from session state
    categories = sorted(list(set([m["category"].strip() for m in materials_data if m.get("category")])))
    
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
                        # Construct normalized local path
                        full_path = os.path.normpath(os.path.join(root_path, material_name))
                        
                        material_map[material_name] = full_path
                        material_options.append(material_name)
                
                if material_options:
                    selected_material = st.selectbox(
                        "Select Material to View",
                        options=material_options,
                        key="materials_selectbox"
                    )
                    
                    if selected_material and selected_material in material_map:
                        full_path = material_map[selected_material]
                        
                        # Display path info
                        st.caption(f"📂 **Path:** `{full_path}`")
                        
                        # Verify local file exists
                        if os.path.exists(full_path):
                            # High-speed native PDF rendering
                            st.pdf(full_path)
                            
                            # Fast download option via memory stream
                            with open(full_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download PDF",
                                    data=f.read(),
                                    file_name=selected_material,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                        else:
                            st.error(f"❌ File not found at: `{full_path}`")
                            st.info("💡 Tip: Ensure the file path and PDF file name match your database entry.")
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
