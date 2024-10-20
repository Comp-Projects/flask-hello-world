from flask import Flask, request, jsonify, render_template
import pandas as pd
from googletrans import Translator
import os

app = Flask(__name__)

# Initialize the translator
translator = Translator()

# Load the CSV file
csv_file_path = "C:/Users/HP/OneDrive/Desktop/Weather/judgments.csv"  # Update this path
try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    print(f"Error loading CSV file: {e}")
    df = pd.DataFrame()  # Initialize an empty DataFrame if loading fails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.form.get('query')
    language = request.form.get('language')

    # Validate input
    if not user_input or user_input.strip() == "":
        return jsonify({'error': 'Query cannot be empty.'})

    # Translate the query to English if it's not in English
    try:
        if language != 'English':
            translated_query = translator.translate(user_input, src=language.lower(), dest='en').text
        else:
            translated_query = user_input
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'})

    # Debug output: Log the translated query
    print(f"Translated query: {translated_query}")

    # Search for relevant cases based on the translated query
    try:
        # Match exactly against case_no column
        results = df[df['case_no'].astype(str).str.contains(translated_query, case=False)]
    except Exception as e:
        return jsonify({'error': f'Error searching the data: {str(e)}'})

    # Generate the response
    if not results.empty:
        response = "🗃️ **Results:**"
        for index, row in results.iterrows():
            case_info = f"""
                <div class="chat-bubble bot-bubble"> 
                    <h5>**Case No:** {row['case_no']}</h5>
                    <p>**Petitioner:** {row['pet']}</p>
                    <p>**Respondent:** {row['res']}</p>
                    <p>**Judgment By:** {row['judgement_by'] if pd.notna(row['judgement_by']) else 'Not Available'}</p>
                    <p>**Judgment Date:** {row['judgment_dates']}</p>
                    <p>**Language:** {row['language'] if pd.notna(row['language']) else 'Not Available'}</p>
                    <p><a href="{row['temp_link']}" target="_blank" rel="noopener noreferrer">📥 Download PDF</a></p>
                </div>
            """
            response += case_info
        return jsonify({'response': response})
    else:
        return jsonify({'response': "🚫 No results found. Please try a different query."})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

