// Citation for the following reference:
// Date: 03/14/2025
// Originality: Referenced
// Source URL: https://www.w3schools.com/js/js_examples.asp
// Description: Referenced for JavaScript examples and syntax usage.



document.addEventListener("DOMContentLoaded", function () {
    console.log("Exercise JavaScript loaded!");

    // ---------------------- Exercise CRUD ----------------------

    // Function to refresh exercise dropdown based on current exercise table
    function refreshExerciseDropdownFromTable() {
        const exerciseTable = document.getElementById("exerciseTable");
        const exerciseDropdown = document.getElementById("exerciseID");

        // Clear current dropdown
        exerciseDropdown.innerHTML = '<option value="">-- Select Exercise --</option>';

        // Populate dropdown from exercise table
        const rows = exerciseTable.querySelectorAll("tr");
        rows.forEach(row => {
            const cells = row.querySelectorAll("td");
            if (cells.length > 0) {
                const exerciseID = cells[0].textContent.trim();
                const name = cells[1].textContent.trim();
                const minutes = cells[2].textContent.trim();
                const calories = cells[3].textContent.trim();

                const option = document.createElement("option");
                option.value = exerciseID;
                option.textContent = name;
                option.dataset.minutes = minutes;
                option.dataset.calories = calories;

                exerciseDropdown.appendChild(option);
            }
        });
    }

    // ---------------------- Delete Exercise ----------------------
    window.deleteExercise = function (exerciseID) {
        if (confirm("Are you sure you want to delete this exercise?")) {
            fetch(`/delete_exercise/${exerciseID}`, { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(`Exercise ${exerciseID} deleted successfully!`);
                        document.getElementById(`exerciseRow-${exerciseID}`).remove();
                        refreshExerciseDropdownFromTable(); // Refresh dropdown
                    } else {
                        alert("Failed to delete exercise.");
                    }
                })
                .catch(error => console.error("Error deleting exercise:", error));
        }
    };

    // ---------------------- Auto-fill Update Form ----------------------
    const exerciseDropdown = document.getElementById("exerciseID");
    const updateExerciseMinutes = document.getElementById("updateExerciseMinutes");
    const updateCaloriesBurned = document.getElementById("updateCaloriesBurned");
    const updateExerciseForm = document.getElementById("updateExerciseForm");

    if (exerciseDropdown) {
        exerciseDropdown.addEventListener("change", function () {
            let selectedExercise = exerciseDropdown.value;
            if (selectedExercise) {
                const selectedOption = exerciseDropdown.querySelector(`option[value="${selectedExercise}"]`);
                if (selectedOption) {
                    updateExerciseMinutes.value = selectedOption.dataset.minutes;
                    updateCaloriesBurned.value = selectedOption.dataset.calories;
                    updateExerciseForm.action = `/update_exercise/${selectedExercise}`;
                }
            } else {
                updateExerciseMinutes.value = "";
                updateCaloriesBurned.value = "";
                updateExerciseForm.action = "";
            }
        });
    }

    // Function to auto-fill update form based on selected exercise
    window.populateUpdateExerciseForm = function (exerciseID) {
        console.log(`Editing exercise ${exerciseID}`);
        exerciseDropdown.value = exerciseID;


        const selectedOption = exerciseDropdown.querySelector(`option[value="${exerciseID}"]`);
        if (selectedOption) {
            const minutes = selectedOption.dataset.minutes;
            const calories = selectedOption.dataset.calories;

            updateExerciseMinutes.value = minutes;
            updateCaloriesBurned.value = calories;
            updateExerciseForm.action = `/update_exercise/${exerciseID}`; 

            console.log(`Auto-filled minutes: ${minutes}, calories: ${calories}`);
        } else {
            console.error("Selected exercise not found in dropdown.");
        }


        updateExerciseForm.scrollIntoView({ behavior: 'smooth' });
    };
});
