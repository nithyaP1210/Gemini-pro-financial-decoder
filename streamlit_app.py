import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration (MUST BE THE FIRST STREAMLIT COMMAND)
st.set_page_config(page_title="Gemini Pro Financial Decoder", layout="wide")

# Inject CSS Styling
st.markdown(
    """
    <style>
        body {
            background-color: #f0f2f6;
            color: #333333;
        }
        .main {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            border-radius: 5px;
            padding: 8px 16px;
        }
        .stDataFrame {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        h1, h2, h3 {
            color: #007bff;
        }
        .block-container {
            padding: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# App title and description
st.title("📊 Gemini Pro Financial Decoder")
st.subheader("Upload a financial report (PDF or Excel) to generate AI-powered insights")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "xlsx", "xls"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "pdf":
        st.info("Uploading PDF file... Please wait.")

        # Send PDF to backend Flask API
        files = {'file': ('report.pdf', uploaded_file.read(), 'application/pdf')}
        try:
            response = requests.post("http://127.0.0.1:5000/upload", files=files)

            if response.status_code == 200:
                data = response.json()

                st.success("✅ PDF Analysis Complete!")

                st.subheader("📑 Financial Summary")
                st.write(data['summary'])

                st.subheader("📊 Financial Metrics")
                financial_df = pd.DataFrame(data['financial_data'].items(), columns=["Metric", "Value"])
                st.dataframe(financial_df)

                # Visualize Financial Metrics
                st.subheader("📈 Financial Visualization")
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(financial_df["Metric"], financial_df["Value"], color='skyblue')
                plt.xticks(rotation=45)
                st.pyplot(fig)

            else:
                st.error(f"❌ Error processing PDF file: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to backend. Is Flask server running?")

    elif file_type in ["xlsx", "xls"]:
        st.info("Reading Excel file...")
        try:
            df = pd.read_excel(uploaded_file)
            st.write("📊 Excel File Preview", df)

        except Exception as e:
            st.error(f"❌ Failed to read Excel file: {e}")
