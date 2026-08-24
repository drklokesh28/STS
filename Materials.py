import streamlit as st
import requests
import urllib.parse
from streamlit_pdf_viewer import pdf_viewer

# Repository Configuration
GITHUB_USER = "drklokesh28"
GITHUB_REPO = "STS"

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pdf_from_github(relative_path: str) -> bytes:
    """
    Fetches raw PDF bytes directly from GitHub.
    Normalizes path slashes and checks both 'main' and 'master' branches to prevent HTTP 404 errors.
    """
    try:
        # 1. Clean up and normalize path slashes (Removes double slashes like '//')
        clean_path = "/".join([part for part in relative_path.replace("\\", "/").split("/") if part.strip()])
        encoded_path = urllib.parse.quote(clean_path)
        
        # 2. Try fetching from 'main' branch first, then fallback to 'master'
        branches = ["main", "master"]
        
        for branch in branches:
            full_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{branch}/{encoded_path}"
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                return response.content

        # If both branches returned 404
        st.error(f"❌ Failed to fetch material from GitHub (HTTP 404 Not Found)")
        st.caption(f"Checked Path: `{clean_path}` across `main` and `master` branches.")
        st.caption(f"Last Attempted URL: `https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{encoded_path}`")
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
    
    # Extract unique categories cleanly
    categories = sorted(list(set([m["category"].strip() for m in materials_data if m.get("category")])))
    
    if not categories:
        st.info("ℹ️ No material categories found.")
        return
    
    # Split layout into two columns
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
                m for m in materials_data if m.get("category", "").strip() == selected_category
            ]
            
            if category_materials:
                st.subheader(f"📄 {selected_category} Materials", divider="blue")
                
                material_options = []
                material_map = {}
                
                for entry in category_materials:
                    raw_files = entry.get("materials", "")
                    root_path = entry.get("root_path", "").strip()
                    
                    # Clean and split comma-separated file names
                    files_list = [f.strip() for f in raw_files.split(",") if f.strip()]
                    
                    for filename in files_list:
                        # Normalize path joining without generating double slashes '//'
                        parts = [p.strip("/") for p in [root_path, filename] if p.strip("/")]
                        github_rel_path = "/".join(parts)
                        
                        material_map[filename] = github_rel_path
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
                        
                        # Fetch PDF bytes with path clean-up
                        with st.spinner("⚡ Fetching material from GitHub..."):
                            pdf_bytes = fetch_pdf_from_github(github_rel_path)
                            
                        if pdf_bytes:
                            # Render PDF with fast byte viewer
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
