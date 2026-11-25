const uploadButton = document.querySelector("button");

uploadButton.addEventListener("click", async function () {

    const fileInput = document.getElementById("audioFile");
    const resultDiv = document.getElementById("result");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a meeting recording first.");
        return;
    }

    resultDiv.textContent = "Uploading and processing your meeting...";

    try {

        const formData = new FormData();
        formData.append("file", file);

        // Step 1: Upload audio and transcribe
        const uploadResponse = await fetch(
            "http://127.0.0.1:8000/upload-audio",
            {
                method: "POST",
                body: formData
            }
        );

        const uploadResult = await uploadResponse.json();

        if (!uploadResponse.ok) {
            throw new Error(uploadResult.detail || "Upload failed");
        }

        const transcript =
            uploadResult.transcription ||
            uploadResult.transcript ||
            uploadResult.text;

        if (!transcript) {
            throw new Error("Transcription not found in upload response.");
        }
        const transcriptionDiv = document.getElementById("transcription");

transcriptionDiv.innerHTML = "";

const transcriptionHeading = document.createElement("h2");
transcriptionHeading.textContent = "Meeting Transcription";

const transcriptionText = document.createElement("p");
transcriptionText.textContent = transcript;

transcriptionDiv.appendChild(transcriptionHeading);
transcriptionDiv.appendChild(transcriptionText);

        // Step 2: Generate AI summary
        const summaryData = new FormData();
        summaryData.append("transcript", transcript);

        const summaryResponse = await fetch(
            "http://127.0.0.1:8000/summarize",
            {
                method: "POST",
                body: summaryData
            }
        );

        const summaryResult = await summaryResponse.json();

        if (!summaryResponse.ok) {
            throw new Error(summaryResult.detail || "Summary generation failed");
        }

        // Step 3: Display results
        resultDiv.innerHTML = "";

        const heading = document.createElement("h2");
        heading.textContent = "Meeting Summary";
        resultDiv.appendChild(heading);

        const summary = document.createElement("div");
        summary.innerHTML = DOMPurify.sanitize(marked.parse(summaryResult.summary || ""));
        resultDiv.appendChild(summary);

        const actionHeading = document.createElement("h3");
        actionHeading.textContent = "Action Items";
        resultDiv.appendChild(actionHeading);

        (summaryResult.action_items || []).forEach(item => {
            const task = document.createElement("p");
            task.textContent =
                "Task: " + item.task +
                " | Owner: " + (item.owner || "Not specified") +
                " | Deadline: " + (item.deadline || "Not specified");

            resultDiv.appendChild(task);
        });

        alert("Meeting summary generated successfully!");

    } catch (error) {

        resultDiv.textContent = "Error: " + error.message;
        alert("Error: " + error.message);

    }

});
async function loadMeetingHistory() {
    const historyDiv = document.getElementById("history");

    try {
        const response = await fetch("http://127.0.0.1:8000/meetings");
        const meetings = await response.json();

        if (!response.ok) {
            throw new Error("Could not load meeting history");
        }

        historyDiv.innerHTML = "<h2>Meeting History</h2>";

        if (meetings.length === 0) {
            historyDiv.innerHTML += "<p>No previous meetings found.</p>";
            return;
        }

        meetings.forEach(meeting => {
            const meetingCard = document.createElement("div");
            meetingCard.className = "meeting-card";

            const title = document.createElement("h3");
            title.textContent = meeting.title || "Untitled Meeting";        
              
            const summary = document.createElement("div");
 summary.innerHTML = DOMPurify.sanitize(marked.parse(meeting.summary || ""));
            const date = document.createElement("p");
            date.textContent = "Created: " + meeting.created_at;

            meetingCard.appendChild(title);

const deleteButton = document.createElement("button");
deleteButton.textContent = "Delete Meeting";

deleteButton.addEventListener("click", async () => {
    const confirmDelete = confirm("Are you sure you want to delete this meeting?");

    if (!confirmDelete) return;

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/meetings/${meeting.id}`,
            { method: "DELETE" }
        );

        if (!response.ok) {
            throw new Error("Could not delete meeting");
        }

        alert("Meeting deleted successfully!");
        loadMeetingHistory();

    } catch (error) {
        alert(error.message);
    }
});

            meetingCard.appendChild(summary);
            meetingCard.appendChild(date);
            meetingCard.appendChild(deleteButton);

            historyDiv.appendChild(meetingCard);
        });

    } catch (error) {
        historyDiv.textContent = "Error loading meeting history: " + error.message;
    }
}

loadMeetingHistory();