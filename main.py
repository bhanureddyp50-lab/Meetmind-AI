import json
import whisper
import shutil
import tempfile
import os
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
from fastapi import FastAPI, UploadFile, File, HTTPException,Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import whisper
import shutil
import tempfile

app = FastAPI()
load_dotenv(override=True)
client = client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load Whisper model
model = whisper.load_model("base")

# Root endpoint
@app.get("/")
def home():
    return {"message": "MeetMind AI Backend Running"}

# Upload audio/video endpoint
@app.post("/upload-audio")
def upload_audio(file: UploadFile = File(...)):
    allowed_extensions = [".mp3", ".wav", ".m4a", ".mp4"]

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format"
        )

    try:

        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:

            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        # Transcribe meeting recording
        result = model.transcribe(
            temp_path,
            language="en"
        )

        return {
            "filename": file.filename,
            "transcription": result["text"],
            "status": "Transcription completed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        file.file.close()
        if "temp_path" in locals():
            Path(temp_path).unlink(missing_ok=True)           
 
@app.post("/summarize")
def summarize_meeting(transcript: str = Form(...)):
    if not transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty"
        )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the meeting. Include key points, decisions and important discussions."
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ]
        )

        summary = response.choices[0].message.content

        action_items = extract_action_items(transcript)

        meeting_id = save_meeting_to_db(
            "Meeting Recording",
            transcript,
            summary
        )

        save_action_items_to_db(meeting_id, action_items)

        return {
            "status": "Summary generated successfully",
            "meeting_id": meeting_id,
            "summary": summary,
            "action_items": action_items
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
             
def extract_action_items(transcript):

    prompt = f"""
Each action item must contain:
- task: description of the task
- owner: assigned person's name, or null if unknown
- deadline: date in YYYY-MM-DD format, or null if unknown

Do not invent tasks, owners, or deadlines.
Do not include decisions or general discussion.

Example:
[
    {{
        "task": "Prepare the project report",
        "owner": "Ravi",
        "deadline": "2026-11-15"
    }}
]

Meeting Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content
    return json.loads(result)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
def save_meeting_to_db(title, transcript, summary):
    conn = get_db_connection()
    cursor = None

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO meetings (title, transcript, summary)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (title, transcript, summary)
        )

        meeting_id = cursor.fetchone()[0]
        conn.commit()
        return meeting_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        conn.close()

def save_action_items_to_db(meeting_id, action_items):
    conn = get_db_connection()
    cursor = None

    try:
        cursor = conn.cursor()

        for item in action_items:
            cursor.execute(
                """
                INSERT INTO action_items
                (meeting_id, task, owner, deadline, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    meeting_id,
                    item.get("task"),
                    item.get("owner"),
                    item.get("deadline"),
                    "Pending"
                )
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        conn.close()