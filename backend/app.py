from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.process_files import process_json_files
from utils.query_handler import handle_user_prompt
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = './uploads'

@app.route('/check-database', methods=['GET'])
def check_database():
    db_path = "database.db"
    if not os.path.exists(db_path):
        return jsonify({"ready": False, "message": "Database file does not exist."})
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='streams';
        """)
        table_exists = cursor.fetchone()
        if not table_exists:
            return jsonify({"ready": False, "message": "The 'streams' table does not exist."})
        cursor.execute("SELECT COUNT(*) FROM streams;")
        count = cursor.fetchone()[0]
        if count > 0:
            return jsonify({"ready": True, "message": "Database is ready."})
        else:
            return jsonify({"ready": False, "message": "The database is empty. Please upload data."})
    except Exception as e:
        return jsonify({"ready": False, "message": f"An error occurred: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    file_paths = []

    for file in files:
        if not file.filename.endswith('.json'):
            return jsonify({"message": f"Invalid file type: {file.filename}. Only JSON files are allowed."}), 400
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        file_paths.append(file_path)

    results, error_occurred = process_json_files(file_paths)

    if error_occurred:
        if os.path.exists("database.db"):
            try:
                os.remove("database.db")
            except Exception as e:
                return jsonify({"message": "Failed to remove the database.", "error": str(e)}), 500
        return jsonify({"message": "Error processing files.", "details": results}), 400

    return jsonify({"message": "All files processed successfully!", "details": results})

@app.route('/query', methods=['POST'])
def query():
    user_prompt = request.json.get('prompt')
    if not user_prompt:
        return jsonify({"message": "Prompt is required."}), 400
    try:
        response = handle_user_prompt(user_prompt)
        return jsonify(response)
    except Exception as e:
        return jsonify({"message": f"An error occurred while processing the query: {str(e)}"}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
