streamlit run streamlit_app.pyimport streamlit as st
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

from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text if text else "No text found."

def summarize_financial_data(text):
    prompt = f"Summarize key financial insights:\n{text[:2000]}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error with OpenAI: {e}"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    summary = summarize_financial_data(extracted_text)

    financial_data = {
        "Revenue (in M)": 500.0,
        "Net Profit (in M)": 120.0,
        "Operating Expense (in M)": 200.0,
        "Gross Margin (in M)": 180.0
    }

    return jsonify({'summary': summary, 'financial_data': financial_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
