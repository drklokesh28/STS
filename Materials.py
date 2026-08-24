import streamlit as st
import requests
from streamlit_pdf_viewer import pdf_viewer

# Remote base path configuration for fast GitHub raw fetching
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO/main/"

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pdf_bytes_from_github(file_url: str) -> bytes:
    """Fetch and cache raw PDF bytes directly from GitHub."""
    try:
        res = requests.get(file_url, timeout=10)
        res.raise_for_status()
        return res.content
    except Exception as e:
        st.error(f"Failed to fetch material: {e}")
        return None

def main_layout():
    st.subheader("📚 Study Materials", divider="orange", text_alignment="center")
    
    materials_data = st.session_state.get("materials")
    if not materials_data:
        st.info("ℹ️ No materials available for this course")
        return
    
    categories = sorted(list({m["category"] for m in materials_data if "category" in m}))
    if not categories:
        st.info("ℹ️ No categories found")
        return

    col1, col2 = st.columns([1, 2], border=True, gap="small")
    
    with col1:
        st.subheader("📁 Categories", divider="blue")
        selected_category = st.pills("Select Category", options=categories, key="materials_category_pills")

    with col2:
        if selected_category:
            category_materials = [m for m in materials_data if m.get("category") == selected_category]
            
            material_map = {}
            for mat in category_materials:
                m_list = [item.strip() for item in mat.get("materials", "").split(",") if item.strip()]
                root_path = mat.get("root_path", "")
                
                for m_name in m_list:
                    # Construct GitHub raw target URL
                    clean_root = root_path.strip("/")
                    full_github_url = f"{GITHUB_RAW_BASE}{clean_root}/{m_name}" if clean_root else f"{GITHUB_RAW_BASE}{m_name}"
                    material_map[m_name] = full_github_url

            if material_map:
                selected_material = st.selectbox("Select Material to View", options=list(material_map.keys()))
                
                if selected_material:
                    target_url = material_map[selected_material]
                    
                    with st.spinner("⚡ Fetching material..."):
                        pdf_bytes = fetch_pdf_bytes_from_github(target_url)
                    
                    if pdf_bytes:
                        pdf_viewer(input=pdf_bytes, key=f"pdf_v_{hash(selected_material)}")
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=selected_material,
                            mime="application/pdf",
                            use_container_width=True
                        )
            else:
                st.info("ℹ️ No materials found in this category")
        else:
            st.info("👈 Please select a category to view materials")

def main1():
    main_layout()
