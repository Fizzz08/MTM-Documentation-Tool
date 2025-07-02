# Streamlit-based Dashboard to interact with FastAPI MTM Endpoints

import streamlit as st
import requests
import pandas as pd
import os


API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/mtm")  

st.set_page_config(page_title="MTM Patient Dashboard", layout="wide")
st.title("MTM Patient Dashboard")

# Fetch all patients
@st.cache_data(show_spinner=False)
def fetch_all_patients():
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching patients: {e}")
        return []

# Fetch patient by ID
def fetch_patient_by_id(transaction_id):
    try:
        response = requests.get(f"{API_BASE_URL}/{transaction_id}")
        response.raise_for_status()
        return response.json()
    except:
        return None

# ✅ Fixed XML download URL
def download_xml_by_id(transaction_id):
    try:
        url = f"{API_BASE_URL}/xml/{transaction_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error downloading XML for patient {transaction_id}: {e}")
        return None

# Download XML for all patients
@st.cache_data(show_spinner=False)
def download_all_xml():
    try:
        url = f"{API_BASE_URL}/xml/all"
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching XML: {e}")
        return None

# Sidebar section
with st.sidebar:
    st.header("Patient Lookup")
    patient_id = st.text_input("Enter Transaction ID")
    if st.button("Fetch Patient by ID"):
        if not patient_id.strip():
            st.warning("Please enter a Transaction ID first.")
        else:
            record = fetch_patient_by_id(patient_id)
            if record:
                st.subheader("Patient Record")

                xml_data = download_xml_by_id(patient_id)
                if xml_data:
                    st.download_button(
                        label="Download XML for this patient",
                        data=xml_data,
                        file_name=f"{patient_id}.xml",
                        use_container_width=True,
                        mime="application/xml"
                    )

                html_rows = ""
                for field, value in record.items():
                    clean_value = str(value).replace("\n", " ").replace("  ", " ")
                    html_rows += f"<tr><th>{field}</th><td>{clean_value}</td></tr>"

                st.markdown(f"""
                    <style>
                        .custom-table-wrapper {{
                            position: relative;
                        }}
                        .custom-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 10px;
                        }}
                        .custom-table th, .custom-table td {{
                            text-align: left;
                            padding: 10px;
                            border-bottom: 1px solid #ddd;
                            vertical-align: top;
                            white-space: nowrap;
                        }}
                        .custom-table th {{
                            width: 30%;
                        }}
                    </style>
                    <div class="custom-table-wrapper">
                        <table class="custom-table">{html_rows}</table>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No patient found with this ID.")

# Main section: display table with pagination
patients = fetch_all_patients()
if patients:
    st.subheader("All Patients (Paginated View)")
    df = pd.DataFrame(patients)

    colA, colB = st.columns([4, 1])
    with colA:
        rows_per_page = st.number_input("Rows per page", min_value=1, max_value=1000, value=10, step=1, key="rows_per_page")
    with colB:
        total_records = len(df)
        total_pages = max((total_records - 1) // rows_per_page + 1, 1)
        if "current_page" not in st.session_state:
            st.session_state.current_page = 1
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=st.session_state.current_page, step=1, key="page_input")
        st.session_state.current_page = page

    st.caption(f"Showing page {page} of {total_pages}")

    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    display_df = df.iloc[start_idx:end_idx].copy()
    for col in display_df.columns:
        display_df[col] = display_df[col].astype(str).str.replace("\n", " ").str.replace("  ", " ")

    st.dataframe(display_df)

    st.markdown("""
        <style>
        .download-container {
            margin-top: 20px;
        }
        .download-button-wrapper {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        </style>
        <div class="download-container">
        <div class="download-button-wrapper">
        <span style='font-weight: bold;'>Download all records:</span>
        </div>
        </div>
    """, unsafe_allow_html=True)

    xml_data = download_all_xml()
    if xml_data:
        st.download_button(
            label="Download All Patients (XML)",
            data=xml_data,
            file_name="all_patients.xml",
            mime="application/xml",
            use_container_width=True
        )
    else:
        st.error("Could not prepare XML data. Please check server.")
else:
    st.warning("No patient records available.")
