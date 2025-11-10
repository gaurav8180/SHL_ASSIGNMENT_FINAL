import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# --- ✅ MUST BE FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="✨ SHL Assessment Recommender", page_icon="📊", layout="wide")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
        /* Global Styles */
        body {
            background-color: #f9fafc;
        }
        .main-title {
            text-align: center;
            color: #2b2d42;
            font-weight: 800;
            font-size: 2.4rem;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #6c757d;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .stTextArea textarea, .stTextInput input {
            border-radius: 10px;
            border: 1px solid #ced4da;
        }
        .stButton>button {
            background: linear-gradient(90deg, #0072ff, #00c6ff);
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            background: linear-gradient(90deg, #0056b3, #00a1c9);
        }
        .recommend-table {
            margin-top: 2rem;
            border-collapse: collapse;
            width: 100%;
        }
        .recommend-table th {
            background-color: #0072ff;
            color: white;
            padding: 10px;
        }
        .recommend-table td {
            background-color: #ffffff;
            padding: 8px;
        }
        .recommend-table tr:nth-child(even) td {
            background-color: #f4f8ff;
        }
        a {
            color: #0072ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 class='main-title'>✨ SHL Assessment Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Enter a job description or provide a job posting URL to get the most relevant SHL assessments.</p>", unsafe_allow_html=True)

# --- Tabs for input methods ---
job_description_tab, url_tab = st.tabs(["📝 Job Description", "🔗 Job URL"])

job_description = ""
url = ""

with job_description_tab:
    job_description = st.text_area("Enter Job Description:", height=180, placeholder="e.g. Seeking a data analyst skilled in Excel, SQL, and Python...")

with url_tab:
    url = st.text_input("Enter Job Description URL:")
    if url:
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            job_description = soup.get_text().strip()
            st.success("✅ Job description successfully extracted from the provided URL.")
        except Exception as e:
            st.error(f"❌ Failed to parse job description from URL: {e}")

# --- Recommendation Button ---
if st.button("🚀 Get Recommendations"):
    if not job_description.strip() and not url.strip():
        st.error("⚠️ Please enter a job description or provide a valid URL.")
    else:
        with st.spinner('🔍 Analyzing job description and fetching SHL recommendations...'):
            api_url = os.environ.get("API_URL", "http://localhost:8000")

            try:
                response = requests.post(
                    f"{api_url}/recommend",
                    json={"job_description": job_description},
                    timeout=120
                )

                if response.status_code == 200:
                    try:
                        response_json = response.json()
                        recommendations = response_json.get("recommendations", [])

                        if recommendations:
                            st.success(f"✅ Found {len(recommendations)} relevant SHL assessments!")

                            # Convert to DataFrame
                            df = pd.DataFrame(recommendations)
                            df = df.rename(columns={
                                "name": "Assessment Name",
                                "url": "URL",
                                "remote_testing_support": "Remote Testing Support",
                                "adaptive_irt_support": "Adaptive/IRT Support",
                                "duration": "Duration",
                                "test_types": "Test Types"
                            })

                            # Drop irrelevant columns
                            df = df.drop(columns=['description'], errors='ignore')

                            # Format test_types
                            if 'Test Types' in df.columns:
                                df['Test Types'] = df['Test Types'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

                            # Make URLs clickable
                            if 'URL' in df.columns:
                                df['URL'] = df['URL'].apply(lambda x: f'<a href="{x}" target="_blank">🔗 View</a>')

                            # Render styled table
                            st.markdown(df.to_html(escape=False, index=False, classes='recommend-table'), unsafe_allow_html=True)

                            # Download CSV
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download Recommendations as CSV",
                                data=csv,
                                file_name="shl_recommendations.csv",
                                mime="text/csv",
                            )
                        else:
                            st.warning("⚠️ No matching assessments found. Try adding more details about the job role and required skills.")
                    except Exception as e:
                        st.error("⚠️ Error processing recommendations. Please try again later.")
                else:
                    st.error(f"⚠️ Backend error (Status {response.status_code}). Please try again later.")
            except requests.exceptions.RequestException:
                st.error("🚫 Connection error: Unable to reach the recommendation service.")
            except Exception as e:
                st.error(f"⚠️ Unexpected error: {e}")

# --- Footer ---
st.markdown("---")
st.caption("💡 Built for SHL Recommendation System Assignment | Powered by FastAPI + Streamlit")
