# MeetMind AI – Intelligent Meeting Action Tracker

## Project Overview
MeetMind AI is an AI-powered meeting assistant that helps users automatically transcribe meeting audio, generate meeting summaries, extract important action items, and store meeting information in a PostgreSQL database.

The main goal is to reduce manual meeting documentation and help teams track important discussions and tasks.

## Technologies Used
- **Programming Language:** Python
- **Backend Framework:** FastAPI
- **Speech Recognition:** OpenAI Whisper
- **AI Integration:** Groq API
- **Database:** PostgreSQL
- **Database Connectivity:** psycopg2
- **API Testing:** Swagger UI

## Key Features
1. **Audio Transcription:** Converts meeting audio into text using Whisper AI.
2. **Meeting Summarization:** Generates concise meeting summaries using Groq AI.
3. **Action Item Extraction:** Identifies important tasks and follow-up activities from meeting transcripts.
4. **Database Storage:** Stores meeting details, transcripts, summaries, and action items in PostgreSQL.
5. **REST API:** Provides endpoints to upload audio and process meeting transcripts.

## Project Workflow
1. User uploads a meeting audio file.
2. Whisper AI converts the audio into text.
3. The transcript is sent to the AI model.
4. Groq AI generates a meeting summary and extracts action items.
5. Meeting information is stored in PostgreSQL.
6. The API returns the processed results.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Checks backend status |
| POST | `/upload-audio` | Uploads audio and generates transcription |
| POST | `/summarize` | Generates summary and extracts action items |

## Database
PostgreSQL database: `meetmind_db`

Main tables:
- `meetings`
- `action_items`

## How to Run the Project

1. Clone the repository:

   ```bash
   git clone https://github.com/bhanureddyp50-lab/Meetmind-AI.git
   ```

2. Open the project folder:

   ```bash
   cd Meetmind-AI
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Install the required Python packages used by the project.

5. Configure your `.env` file with your Groq API key and PostgreSQL database credentials. Never upload this file to GitHub.

6. Start the FastAPI server:

   ```bash
   python -m uvicorn main:app --reload
   ```

7. Open the API documentation:

   `http://127.0.0.1:8000/docs`

## Future Enhancements
- Develop a user-friendly frontend.
- Integrate Google Calendar and Google Meet.
- Automate meeting attendance and recording.
- Send meeting summaries through email.
- Add user authentication and meeting history.

## Project Status
Backend core development and testing completed. Frontend and additional automation features are planned for future development.

## Author
Developed as a B.Tech Information Technology project.