import sqlite3
import json

def validate_json_entry(entry, required_keys):
    """Validate a single JSON entry against the required keys."""
    for key in required_keys:
        if key not in entry:
            return False, f"Missing key: {key}"
    return True, ""

def process_json_files(file_paths):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS streams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        platform TEXT,
        ms_played INTEGER,
        conn_country TEXT,
        master_metadata_track_name TEXT,
        master_metadata_album_artist_name TEXT,
        master_metadata_album_album_name TEXT,
        spotify_track_uri TEXT,
        reason_start TEXT,
        reason_end TEXT,
        shuffle BOOLEAN,
        skipped BOOLEAN,
        offline BOOLEAN,
        offline_timestamp INTEGER,
        incognito_mode BOOLEAN
    )
    """)

    required_keys = {
        "ts", "platform", "ms_played", "conn_country",
        "master_metadata_track_name", "master_metadata_album_artist_name",
        "master_metadata_album_album_name", "spotify_track_uri",
        "reason_start", "reason_end", "shuffle", "skipped",
        "offline", "offline_timestamp", "incognito_mode"
    }

    results = []
    error_occurred = False

    for file_path in file_paths:
        if not file_path.endswith('.json'):
            results.append({"file": file_path, "status": "error", "message": "File is not a JSON file."})
            error_occurred = True
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                if not isinstance(data, list):
                    results.append({"file": file_path, "status": "error", "message": "File does not contain a list of entries."})
                    error_occurred = True
                    continue

                for index, entry in enumerate(data):
                    is_valid, error_message = validate_json_entry(entry, required_keys)
                    if not is_valid:
                        results.append({
                            "file": file_path,
                            "status": "error",
                            "message": f"Entry {index + 1} missing key: {error_message}"
                        })
                        error_occurred = True
                        break

                if not error_occurred:
                    for entry in data:
                        if not all([
                            entry.get("master_metadata_track_name"),
                            entry.get("master_metadata_album_artist_name"),
                            entry.get("master_metadata_album_album_name")
                        ]):
                            continue

                        cursor.execute("""
                            INSERT INTO streams (
                                ts, platform, ms_played, conn_country,
                                master_metadata_track_name, master_metadata_album_artist_name,
                                master_metadata_album_album_name, spotify_track_uri, reason_start,
                                reason_end, shuffle, skipped, offline, offline_timestamp, incognito_mode
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            entry.get("ts"), entry.get("platform"), entry.get("ms_played"),
                            entry.get("conn_country"), entry.get("master_metadata_track_name"),
                            entry.get("master_metadata_album_artist_name"),
                            entry.get("master_metadata_album_album_name"),
                            entry.get("spotify_track_uri"), entry.get("reason_start"),
                            entry.get("reason_end"), entry.get("shuffle"), entry.get("skipped"),
                            entry.get("offline"), entry.get("offline_timestamp"),
                            entry.get("incognito_mode")
                        ))

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            results.append({"file": file_path, "status": "error", "message": str(e)})
            error_occurred = True

    conn.commit()
    conn.close()

    return results, error_occurred
