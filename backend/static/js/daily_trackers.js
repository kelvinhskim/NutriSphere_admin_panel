let trackers = {}; // Object to store all daily tracker data

// Function to load tracker data passed from Flask (Jinja2)
function loadTrackers(data) {
    trackers = data;
}

// Function to auto-fill calorie goal when a user is selected in the Add Tracker form
function getSelectedUserCalorieGoal() {
    const selectedUser = document.getElementById("selectedUser");
    const calorieGoal = selectedUser.options[selectedUser.selectedIndex].getAttribute("data-calorie-goal");
    document.getElementById("calorieGoal").value = calorieGoal;
}

// Update Form - Auto-populate fields when selecting a tracker to edit
function getSelectedTracker() {
    const trackerID = document.getElementById("selectedTracker").value;
    const tracker = trackers[trackerID];

    if (tracker) {
        document.getElementById("update-user-id").value = tracker.userID;
        document.getElementById("update-date").value = tracker.date;
        document.getElementById("update-calorie-goal").value = tracker.calorieGoal;
        document.getElementById("update-exercise").value = tracker.exerciseID || "NULL"; // handle null case
    }
}

// Populate update form when clicking Edit button
function populateUpdateTracker(trackerID) {
    const tracker = trackers[trackerID];
    if (tracker) {
        document.getElementById("selectedTracker").value = trackerID;
        getSelectedTracker(); // Populate the rest
        document.getElementById("update-tracker-form").scrollIntoView({ behavior: 'smooth' });
    }
}

// Submit PUT request to update Daily Tracker
function submitUpdateTracker() {
    const trackerID = document.getElementById("selectedTracker").value;

    const data = {
        userID: document.getElementById("update-user-id").value,
        date: document.getElementById("update-date").value,
        calorieGoal: document.getElementById("update-calorie-goal").value,
        exerciseID: document.getElementById("update-exercise").value
    };

    fetch(`/daily-trackers/${trackerID}`, {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) return response.json();
        throw new Error("Failed to update tracker.");
    })
    .then(data => window.location.href = data.redirect_url)
    .catch(error => console.error("Error updating tracker:", error));
}

// DELETE request to remove a tracker
function deleteTracker(trackerID, username, date) {
    if (confirm(`Are you sure you want to delete the tracker for ${username} on ${date}?`)) {
        console.log("Deleting tracker ID:", trackerID);
        fetch(`/daily-trackers/${trackerID}`, { method: "DELETE" })
            .then(response => {
                if (response.ok) return response.json();
                throw new Error("Failed to delete tracker.");
            })
            .then(data => {
                console.log("Tracker deleted:", data);
                window.location.href = data.redirect_url; 
            })
            .catch(error => console.error("Error deleting tracker:", error));
    }
}