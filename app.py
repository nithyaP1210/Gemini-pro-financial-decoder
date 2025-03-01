import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Gemini Pro Financial Decoder", layout="wide")
st.title("📊 Gemini Pro Financial Decoder")
st.subheader("Upload a financial report (PDF or Excel) to generate AI-powered insights")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "xlsx", "xls"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type in ["pdf"]:
        st.info("Uploading PDF file... Please wait.")
        
        # Send PDF file to Flask API
        files = {'file': ('report.pdf', uploaded_file.read(), 'application/pdf')}

        try:
            response = requests.post("http://127.0.0.1:5000/upload", files=files)

            if response.status_code == 200:
                data = response.json()
                st.success("✅ PDF Analysis Complete!")

                # Display Financial Summary
                st.subheader("📑 Financial Summary")
                st.write(data['summary'])

                # Display Financial Metrics
                st.subheader("📊 Financial Metrics")
                financial_df = pd.DataFrame(data['financial_data'].items(), columns=["Metric", "Value"])
                st.dataframe(financial_df)

                # Visualize Metrics
                st.subheader("📈 Financial Summary Visualization")
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(financial_df["Metric"], financial_df["Value"], color='skyblue')
                ax.set_xlabel("Financial Metrics")
                ax.set_ylabel("Value (in millions)")
                ax.set_title("Financial Summary Visualization")
                plt.xticks(rotation=45)
                st.pyplot(fig)

            else:
                st.error(f"❌ Error processing PDF file: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the backend API. Make sure Flask server is running.")

    elif file_type in ["xlsx", "xls"]:
        st.info("Processing Excel file...")

        # Read Excel file into DataFrame
        try:
            excel_df = pd.read_excel(uploaded_file)
            st.subheader("📊 Excel Data Preview")
            st.dataframe(excel_df)

            # Example - Check if key financial metrics exist in Excel data
            st.subheader("📈 Key Metrics from Excel (if present)")
            financial_metrics = ["Revenue", "Net Profit", "Operating Expense", "Gross Margin"]

            extracted_metrics = {}
            for metric in financial_metrics:
                # Example logic: look for rows with these metric names
                matched_rows = excel_df[excel_df.apply(lambda row: row.astype(str).str.contains(metric, case=False, na=False).any(), axis=1)]
                if not matched_rows.empty:
                    # Just taking first match for simplicity
                    value = matched_rows.iloc[0, 1]  # Assuming value is in second column
                    extracted_metrics[metric] = value

            if extracted_metrics:
                financial_df = pd.DataFrame(extracted_metrics.items(), columns=["Metric", "Value"])
                st.dataframe(financial_df)

                # Visualize Excel Metrics
                st.subheader("📊 Financial Summary Visualization (from Excel)")
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(financial_df["Metric"], financial_df["Value"], color='green')
                ax.set_xlabel("Financial Metrics")
                ax.set_ylabel("Value")
                ax.set_title("Financial Summary Visualization (Excel)")
                plt.xticks(rotation=45)
                st.pyplot(fig)

            else:
                st.warning("⚠️ No key financial metrics found in Excel file.")

        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")

