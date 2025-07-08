import streamlit as st
import requests
import pandas as pd
import os

API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/mtm")  
NCPDP_BASE_URL = f"{API_BASE_URL}/ncpdp/messaging"
MESSAGING_EXPORT_URL = f"{API_BASE_URL}/messaging/all"

st.set_page_config(page_title="MTM Patient Dashboard", layout="wide")

# --- Load external CSS ---
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("sidebar.css")

# --- Initialize Session State ---
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "patients"

# --- Sidebar Navigation ---
pages = {
    "🏠 All Patients": "patients",
    "🔍 Search by ID": "search",
    "🔑 Demographics": "demographics"
}

with st.sidebar:
    st.markdown("<div class='sidebar'>", unsafe_allow_html=True)
    st.markdown("<h2>Menu</h2>", unsafe_allow_html=True)
    for label, value in pages.items():
        button_class = "sidebar-item active" if st.session_state.nav_page == value else "sidebar-item"
        if st.button(label, key=value):
            st.session_state.nav_page = value
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main Content ---
st.title("MTM Patient Dashboard")
selected_page = st.session_state.nav_page

# --- API Functions ---
@st.cache_data(show_spinner=False)
def fetch_all_patients():
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching patients: {e}")
        return []

def fetch_patient_by_id(patient_id):
    try:
        response = requests.get(f"{API_BASE_URL}/{patient_id}")
        response.raise_for_status()
        return response.json()
    except:
        return None

@st.cache_data(show_spinner=False)
def download_all_xml():
    try:
        response = requests.get(f"{API_BASE_URL}/xml/all")
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching XML: {e}")
        return None

def download_xml_by_id(patient_id):
    url = f"{API_BASE_URL}/{patient_id}/xml"
    response = requests.get(url)
    return response.text if response.ok else None

def download_ncpdp_by_id(patient_id):
    url = f"{NCPDP_BASE_URL}/download/{patient_id}"
    response = requests.get(url)
    return response.text if response.ok else None

def download_all_ncpdp():
    try:
        response = requests.get(MESSAGING_EXPORT_URL)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching NCPDP message format: {e}")
        return None

def fetch_demographic_by_key(patient_id, key):
    try:
        url = f"{NCPDP_BASE_URL}/{patient_id}/{key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Not found")}
    except Exception as e:
        return {"error": str(e)}

# --- Page Logic ---
if selected_page == "patients":
    patients = fetch_all_patients()
    if patients:
        st.subheader("📋 All Patients (Paginated View)")
        df = pd.DataFrame(patients)

        colA, colB = st.columns([4, 1])
        with colA:
            rows_per_page = st.number_input("Rows per page", min_value=1, max_value=1000, value=10)
        with colB:
            total_records = len(df)
            total_pages = max((total_records - 1) // rows_per_page + 1, 1)
            if "current_page" not in st.session_state:
                st.session_state.current_page = 1
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=st.session_state.current_page)
            st.session_state.current_page = page

        st.caption(f"Showing page {page} of {total_pages}")
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        display_df = df.iloc[start_idx:end_idx].copy()
        for col in display_df.columns:
            display_df[col] = display_df[col].astype(str).str.replace("\n", " ").str.replace("  ", " ")
        st.dataframe(display_df)

        format_choice = st.selectbox("Choose Format to Download All", ["NCPDP XML Format", "NCPDP Messaging Format"], key="all_format")
        if format_choice == "NCPDP XML Format":
            xml_data = download_all_xml()
            if xml_data:
                st.download_button("Download All Patients (XML)", data=xml_data, file_name="all_patients.xml", mime="application/xml")
        else:
            ncpdp_data = download_all_ncpdp()
            if ncpdp_data:
                st.download_button("Download All Patients (NCPDP Messaging Format)", data=ncpdp_data, file_name="all_patients.txt", mime="text/plain")
    else:
        st.warning("No patient records available.")

elif selected_page == "search":
    st.subheader("🔍 Search Patient by Patient ID")
    patient_id = st.text_input("Enter Patient ID")
    if patient_id:
        record = fetch_patient_by_id(patient_id)
        if record:
            st.success(f"Patient found: {patient_id}")
            download_format = st.selectbox("Choose Format", ["NCPDP XML Format", "NCPDP Messaging Format"])
            if download_format == "NCPDP XML Format":
                st.download_button("Download XML", data=download_xml_by_id(patient_id), file_name=f"{patient_id}.xml", mime="application/xml")
            else:
                st.download_button("Download Messaging Format", data=download_ncpdp_by_id(patient_id), file_name=f"{patient_id}.txt", mime="text/plain")

            html_rows = ""
            for field, value in record.items():
                clean_value = str(value).replace("\n", " ").replace("  ", " ")
                html_rows += f"<tr><th>{field}</th><td>{clean_value}</td></tr>"

            st.markdown(f"""
                <div class="custom-table-wrapper">
                    <table class="custom-table">{html_rows}</table>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Patient not found.")

elif selected_page == "demographics":
    st.subheader("🔑 Search Patient Demographic Field")
    with st.form("demo_search_form"):
        col1, col2 = st.columns(2)
        with col1:
            key_patient_id = st.text_input("Enter Patient ID", key="demo_pid")
        with col2:
            key_name = st.text_input("Enter Key (e.g., DOB, ZIP)", key="demo_key")
        submitted = st.form_submit_button("Search")

    if submitted:
        if key_patient_id.strip() and key_name.strip():
            result = fetch_demographic_by_key(key_patient_id, key_name)
            if "error" in result:
                st.error(result["error"])
            else:
                value = result.get(key_name.upper(), "")
                st.success(f"{key_name.upper()} = {value}")
        else:
            st.warning("Please fill both Patient ID and Key fields.")

st.markdown("</div>", unsafe_allow_html=True)
