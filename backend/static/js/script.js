document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript loaded!");

    // Function to refresh user dropdown based on current user table
    function refreshUserDropdownFromTable() {
        const userTable = document.getElementById("userTable");
        const userDropdown = document.getElementById("userID");

        // Clear current dropdown
        userDropdown.innerHTML = '<option value="">-- Select User --</option>';

        // Populate dropdown from user table
        const rows = userTable.querySelectorAll("tr");
        rows.forEach(row => {
            const cells = row.querySelectorAll("td");
            if (cells.length > 0) {
                const userID = cells[0].textContent.trim();
                const username = cells[1].textContent.trim();
                const email = cells[2].textContent.trim();
                const calorieGoal = cells[3].textContent.trim();

                const option = document.createElement("option");
                option.value = userID;
                option.textContent = username;
                option.dataset.email = email;
                option.dataset.goal = calorieGoal;

                userDropdown.appendChild(option);
            }
        });
    }

    // User CRUD (Users Page)
    if (document.getElementById("userTable")) {
        console.log("Users page detected.");

        // Delete User (AJAX) and refresh dropdown after deletion
        window.deleteUser = function (userID) {
            if (confirm("Are you sure you want to delete this user?")) {
                fetch(`/delete_user/${userID}`, { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message) {
                            alert(`User ${userID} deleted successfully!`);
                            document.getElementById(`userRow-${userID}`).remove();
                            refreshUserDropdownFromTable();  // Refresh dropdown
                        } else {
                            alert("Failed to delete user.");
                        }
                    })
                    .catch(error => console.error("Error deleting user:", error));
            }
        };

        // Auto-fill update form when selecting a user from dropdown
        const userDropdown = document.getElementById("userID");
        const updateEmail = document.getElementById("updateEmail");
        const updateCalorieGoal = document.getElementById("updateCalorieGoal");
        const updateForm = document.getElementById("updateUserForm");

        if (userDropdown) {
            userDropdown.addEventListener("change", function () {
                let selectedUser = userDropdown.value;
                if (selectedUser) {
                    const selectedOption = userDropdown.querySelector(`option[value="${selectedUser}"]`);
                    if (selectedOption) {
                        updateEmail.value = selectedOption.dataset.email;
                        updateCalorieGoal.value = selectedOption.dataset.goal;
                        updateForm.action = `/update_user/${selectedUser}`;
                    }
                } else {
                    updateEmail.value = "";
                    updateCalorieGoal.value = "";
                    updateForm.action = `/update_user/0`;
                }
            });
        }

        // "Edit" button in user table to auto-select user in update form
        window.populateUpdateForm = function (userID) {
            console.log(`Editing user ${userID}`);
            // Select the user in the dropdown
            userDropdown.value = userID;

            // Get corresponding option's data
            const selectedOption = userDropdown.querySelector(`option[value="${userID}"]`);
            if (selectedOption) {
                const email = selectedOption.dataset.email;
                const goal = selectedOption.dataset.goal;

                updateEmail.value = email;
                updateCalorieGoal.value = goal;
                updateForm.action = `/update_user/${userID}`;

                console.log(`Auto-filled email: ${email}, goal: ${goal}`);
            } else {
                console.error("Selected user not found in dropdown.");
            }

            // Scroll into view for better UX
            updateForm.scrollIntoView({ behavior: 'smooth' });
        };
    }

    // Daily Trackers CRUD (Daily Trackers Page)
    if (document.getElementById("dailyTrackersTable")) {
        console.log("Daily Trackers page detected.");

        window.deleteTracker = function (trackerID) {
            if (confirm("Are you sure you want to delete this tracker?")) {
                fetch(`/delete_tracker/${trackerID}`, { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message) {
                            alert(`Tracker ${trackerID} deleted successfully!`);
                            document.getElementById(`trackerRow-${trackerID}`).remove();
                        } else {
                            alert("Failed to delete tracker.");
                        }
                    })
                    .catch(error => console.error("Error deleting tracker:", error));
            }
        };
    }

    // Food Items CRUD (Food Items Page)
    if (document.getElementById("foodItemsTable")) {
        console.log("Food Items page detected.");

        window.deleteFoodItem = function (foodItemID) {
            if (confirm("Are you sure you want to delete this food item?")) {
                fetch(`/delete_food_item/${foodItemID}`, { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message) {
                            alert(`Food Item ${foodItemID} deleted successfully!`);
                            document.getElementById(`foodRow-${foodItemID}`).remove();
                        } else {
                            alert("Failed to delete food item.");
                        }
                    })
                    .catch(error => console.error("Error deleting food item:", error));
            }
        };
    }
});
