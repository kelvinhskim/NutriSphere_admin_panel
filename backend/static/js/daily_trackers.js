// Citation for getSelectedTracker function:
// Date: 03/17/2025
// Adapted the method to convert date format from
// Source URL: https://stackoverflow.com/questions/51985791/convert-date-string-with-timezone-to-format-yyyy-mm-dd

// Citation for Fetch API:
// Date: 03/11/2025
// Adapted from Making a Request with Fetch Following Redirects from Flask documentation
// Copied from Handling Response Status Codes from GeeksForGeeks
// Combined code from listed sources for functions to handle PUT and DELETE requests
// Source URL: https://flask.palletsprojects.com/en/stable/patterns/javascript/#making-a-request-with-fetch
// Source URL: https://www.geeksforgeeks.org/javascript-fetch-method/

let trackers = {}; // Object to store all daily tracker data

// Function to load tracker data passed from Flask (Jinja2)
function loadTrackers(data) {
    data.forEach(tracker => {
        trackers[tracker.dailyTrackerID] = tracker
    }) 
    // console.log("Loaded trackers:", trackers)
}

// Add Tracker Form - Function to auto-fill user's default calorie goal when a user is selected from the dropdown
function getSelectedUserCalorieGoal() {
    const selectedUser = document.getElementById("selectedUser");
    const calorieGoal = selectedUser.options[selectedUser.selectedIndex].getAttribute("data-calorie-goal");
    document.getElementById("calorieGoal").value = calorieGoal;
}

// Update Form - Auto-populate fields when selecting a tracker using the dropdown 
function getSelectedTracker() {
    const trackerID = document.getElementById("selectedTracker").value;
    const tracker = trackers[trackerID];

    // set date as retrieved date in GMT datetime format
    let date = tracker.date

    // parse date string
    const [day, dd, m, yyyy, ...time] = date.split(' ');
    
    // convert date and month values
    const format = (d) => (d < 10 ? '0' : '') + d; // two digit format for date
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const mm = format(months.indexOf(m) + 1); // convert month text to number

    // format date as yyyy-mm-dd
    date = `${yyyy}-${mm}-${dd}`;

    if (tracker) {
        document.getElementById("update-user-id").value = tracker.userID;
        document.getElementById("update-date").value = date;
        document.getElementById("update-calorie-goal").value = tracker.calorieGoal;
        document.getElementById("update-exercise").value = tracker.exerciseID || "NULL"; // handle null case
    }
}

// Update Form - Auto-populates fields when selecting a tracker by clicking the Edit button
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