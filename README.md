# summarization_app

A simple web application that takes links to articles and summarizes them for the user.

## Features
- Enter a URL to an article and receive a concise summary.
- User-friendly interface built with Streamlit.
- Option to analyze and display multiple article summaries in a session.
- Download CSV of analyzed articles and summaries.

## How It Works
1. Enter the link to the article you want summarized.
2. Click the "Analyze" button.
3. The app fetches and summarizes the article content.
4. Summaries are displayed in the app and can be downloaded as a CSV file.

## Requirements
- Python 3.7+
- streamlit
- pandas
- (other dependencies as required by your code)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Running the App
```bash
streamlit run app.py
```

## Project Structure
- `app.py` - Main application file.
- `requirements.txt` - Python dependencies.

## License
This project is licensed under the MIT License.
