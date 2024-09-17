import os
import re
import csv
from flask import Flask, render_template, request, redirect, url_for, send_file
from PyPDF2 import PdfReader
import pandas as pd

app = Flask(__name__)

# Create a folder to store uploaded PDFs
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to extract emails from the PDF text
def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Return unique emails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extract text from PDF
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

        # Extract emails from the text
        emails = extract_emails(text)

        # Save emails to CSV
        if emails:
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'emails.csv')
            df = pd.DataFrame(emails, columns=["emails"])
            df.to_csv(csv_path, index=False)

            return render_template('result.html', emails=emails, csv_path='emails.csv')
        else:
            return render_template('result.html', emails=None)

    return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
