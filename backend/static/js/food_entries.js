// Preload food entries for editing
let foodEntries = {}

function loadFoodEntries(entries) {
    foodEntries = entries.reduce((acc, entry) => {
        acc[entry.foodEntryID] = {
            mealCategory: entry.mealCategory,
            foodItemID: entry.foodItemID,
            dailyTrackerID: entry.dailyTrackerID
        };
        return acc;
    }, {});
}

// Populate update form when edit button clicked
function populateUpdateFoodEntry(id) {
    const entry = foodEntries[id];
    document.getElementById("selected-food-entry-id").value = id;
    document.getElementById("update-meal-category").value = entry.mealCategory;
    document.getElementById("update-food-item-id").value = entry.foodItemID;
    document.getElementById("update-daily-tracker-id").value = entry.dailyTrackerID;
}

// Sync update form when entry selected from dropdown
function getSelectedFoodEntry() {
    const id = document.getElementById("selected-food-entry-id").value;
    populateUpdateFoodEntry(id);
}

// Submit update via PUT
function submitUpdateFoodEntry() {
    const id = document.getElementById("selected-food-entry-id").value;
    const data = {
        mealCategory: document.getElementById("update-meal-category").value,
        foodItemID: document.getElementById("update-food-item-id").value,
        dailyTrackerID: document.getElementById("update-daily-tracker-id").value
    };

    fetch(`/food-entries/${id}`, {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.ok ? response.json() : Promise.reject(response.status))
    .then(response => window.location = response.redirect_url)
    .catch(console.error);
}

// Delete entry via DELETE
function deleteFoodEntry(id, mealCategory, food, dailyTracker) {
    if (confirm(`Delete this entry?\nID: ${id}\nMeal: ${mealCategory}\nFood: ${food}\nTracker: ${dailyTracker}`)) {
        fetch(`/food-entries/${id}`, { method: "DELETE" })
            .then(response => response.ok ? response.json() : Promise.reject(response.status))
            .then(response => window.location = response.redirect_url)
            .catch(console.error);
    }
}
