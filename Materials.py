import streamlit as st
import requests
import urllib.parse
from streamlit_pdf_viewer import pdf_viewer

# Repository configuration for GitHub Raw fetching
GITHUB_USER = "drklokesh28"
GITHUB_REPO = "STS"
GITHUB_BRANCH = "main"

BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/"

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pdf_from_github(file_path: str) -> bytes:
    """
    Fetches raw PDF bytes directly from the drklokesh28/STS GitHub repository.
    Caches the binary data locally to ensure zero-lag repeat rendering.
    """
    try:
        # Sanitize path and handle spacing or special characters
        clean_path = file_path.strip().lstrip("/")
        encoded_path = urllib.parse.quote(clean_path)
        full_url = f"{BASE_RAW_URL}{encoded_path}"
        
        response = requests.get(full_url, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"❌ Failed to fetch material from GitHub (HTTP {response.status_code})")
            st.caption(f"Target URL: `{full_url}`")
            return None
    except Exception as e:
        st.error(f"❌ Network error while retrieving PDF: {str(e)}")
        return None


def main_layout():
    """
    Main layout for the Study/Materials section.
    Displays PDF materials organized by category dynamically loaded from GitHub.
    """
    st.subheader("📚 Study Materials", divider="orange", text_alignment="center")
    
    # Verify materials in session state
    materials_data = st.session_state.get("materials")
    if not materials_data:
        st.info("ℹ️ No study materials available for this selected course.")
        return
    
    # Extract categories
    categories = sorted(list(set([material["category"] for material in materials_data if "category" in material])))
    
    if not categories:
        st.info("ℹ️ No material categories found.")
        return
    
    # Split interface layout
    col1, col2 = st.columns([1, 2], border=True, gap="small")
    
    # Column 1: Category selection
    with col1:
        st.subheader("📁 Categories", divider="blue")
        selected_category = st.pills(
            "Select Category",
            options=categories,
            selection_mode="single",
            key="materials_category_pills"
        )

    # Column 2: File selection & rendering
    with col2:
        if selected_category:
            category_materials = [
                m for m in materials_data if m.get("category") == selected_category
            ]
            
            if category_materials:
                st.subheader(f"📄 {selected_category} Materials", divider="blue")
                
                material_options = []
                material_map = {}
                
                for entry in category_materials:
                    raw_files = entry.get("materials", "")
                    root_path = entry.get("root_path", "").strip()
                    
                    # Split comma-separated file entries
                    files_list = [f.strip() for f in raw_files.split(",") if f.strip()]
                    
                    for filename in files_list:
                        # Build relative path inside the repo
                        if root_path:
                            rel_path = f"{root_path}/{filename}".replace("\\", "/")
                        else:
                            rel_path = filename
                            
                        material_map[filename] = rel_path
                        material_options.append(filename)
                
                if material_options:
                    selected_file = st.selectbox(
                        "Select Material to View",
                        options=material_options,
                        key="materials_selectbox"
                    )
                    
                    if selected_file:
                        github_rel_path = material_map[selected_file]
                        st.caption(f"🔗 **Repository File:** `{GITHUB_USER}/{GITHUB_REPO}/{github_rel_path}`")
                        
                        # High-speed cached fetch
                        with st.spinner("⚡ Fetching material from GitHub..."):
                            pdf_bytes = fetch_pdf_from_github(github_rel_path)
                            
                        if pdf_bytes:
                            # Render PDF with instant byte viewer
                            pdf_viewer(
                                input=pdf_bytes,
                                key=f"pdf_viewer_{hash(selected_file)}"
                            )
                            
                            # Instant Download Option
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_bytes,
                                file_name=selected_file,
                                mime="application/pdf",
                                use_container_width=True
                            )
                else:
                    st.info("ℹ️ No materials found in this category.")
            else:
                st.info("ℹ️ No materials found for the selected category.")
        else:
            st.info("👈 Select a category from the left pane to view materials.")


def main1():
    """Wrapper entry point for mainFile.py integration."""
    main_layout()


if __name__ == "__main__":
    main_layout()
