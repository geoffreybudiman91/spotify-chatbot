import openai
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_sql_query(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are an assistant that generates SQL queries based on user input."},
                {"role": "user", "content": f"Generate an SQL query to answer this prompt: '{prompt}' "
                                             f"for a database with the following schema:\n"
                                             f"streams(id INTEGER, ts TEXT, platform TEXT, "
                                             f"ms_played INTEGER, conn_country TEXT,"
                                             f"master_metadata_track_name TEXT, "
                                             f"master_metadata_album_artist_name TEXT, "
                                             f"master_metadata_album_album_name TEXT, spotify_track_uri TEXT, "
                                             f"reason_start TEXT, reason_end TEXT, shuffle BOOLEAN, "
                                             f"skipped BOOLEAN, offline BOOLEAN, offline_timestamp INTEGER, "
                                             f"incognito_mode BOOLEAN). No need for explanation. Just return, "
                                             f"the SQL Query so I can access the query through response['choices'][0].message.content"
                                             f"If the user prompt includes a song title or artist name, ignore capitalization "
                                             f"No additional formatting like Markdown or comments, just the SQL query."}
            ],
            temperature=0.3
        )
        query = response.choices[0].message.content
        return query.strip()
    except openai.OpenAIError as e:
        return f"Error generating query: {str(e)}"

def execute_sql_query(query):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        return f"Database error: {e}"

def generate_chatbot_response(prompt, query, results):
    try:
        formatted_results = "\n".join([str(row) for row in results]) if results else "No data found."
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that answers user questions based on query results."},
                {"role": "user", "content": f"User asked: '{prompt}'. "
                                             f"The SQL query generated was: '{query}'. "
                                             f"The query results are: {formatted_results}. "
                                             f"Generate a clear and concise response to the user based on these results."
                                             f"Sound friendly, don't just say the answer."}
            ],
            temperature=0.5
        )
        chatbot_response = response.choices[0].message.content
        return chatbot_response.strip()
    except openai.OpenAIError as e:
        return f"Error generating chatbot response: {str(e)}"

def handle_user_prompt(prompt):
    query = generate_sql_query(prompt)
    if "Error" in query:
        return {"error": query}

    results = execute_sql_query(query)
    if isinstance(results, str) and "Database error" in results:
        return {"error": results}

    chatbot_response = generate_chatbot_response(prompt, query, results)
    if "Error" in chatbot_response:
        return {"error": chatbot_response}

    return {
        "query": query,
        "results": results,
        "chatbot_response": chatbot_response
    }
