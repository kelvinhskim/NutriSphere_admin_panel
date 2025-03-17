let trackers = {}; // Object to store all daily tracker data

// Function to load tracker data passed from Flask (Jinja2)
function loadTrackers(data) {
    trackers = data;
}

// Function to auto-fill calorie goal when a user is selected in the Add Tracker form
function setCalorieGoal() {
    const select = document.getElementById("addUserSelect");
    const calorieGoal = select.options[select.selectedIndex].getAttribute("data-calorie-goal");
    document.getElementById("addCalorieGoal").value = calorieGoal;
}

// Function to auto-populate fields in the Update Tracker form when a tracker is selected
function populateTrackerFields() {
    const id = document.getElementById("updateSelect").value;
    const tracker = trackers[id];
    document.getElementById("updateTrackerID").value = id;
    document.getElementById("updateUser").value = tracker.userID;
    document.getElementById("updateDate").value = tracker.date;
    document.getElementById("updateCalorieGoal").value = tracker.calorieGoal;
    document.getElementById("updateExercise").value = tracker.exerciseID || "NULL"; // Handle NULL exercises
}

// Function to auto-populate the Update Tracker form when the Edit button is clicked
function populateUpdateTrackerForm(id) {
    const tracker = trackers[id];
    document.getElementById("updateSelect").value = id;
    populateTrackerFields();
}

// Function to submit an update request for a daily tracker (PUT request)
function submitUpdateTracker() {
    const id = document.getElementById("updateTrackerID").value;
    const data = {
        userID: document.getElementById("updateUser").value,
        date: document.getElementById("updateDate").value,
        calorieGoal: document.getElementById("updateCalorieGoal").value,
        exerciseID: document.getElementById("updateExercise").value
    };
    fetch(`/daily-trackers/${id}`, {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => window.location = res.redirect_url) // Redirect on success
    .catch(error => console.error("Error updating tracker:", error));
}

// Function to delete a daily tracker (DELETE request)
function deleteTracker(id) {
    if (confirm("Are you sure you want to delete this tracker?")) {
        fetch(`/daily-trackers/${id}`, { method: "DELETE" })
            .then(res => res.json())
            .then(res => window.location = res.redirect_url) // Redirect on success
            .catch(error => console.error("Error deleting tracker:", error));
    }
}