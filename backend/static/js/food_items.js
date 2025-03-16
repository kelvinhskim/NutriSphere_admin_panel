document.addEventListener("DOMContentLoaded", function () {
    console.log("Food Items JavaScript loaded!");

    const foodDropdown = document.getElementById("foodID");
    const updateName = document.getElementById("updateName"); 
    const updateBrand = document.getElementById("updateBrand");
    const updateServingSize = document.getElementById("updateServingSize");
    const updateCalories = document.getElementById("updateCalories");
    const updateProtein = document.getElementById("updateProtein");
    const updateFat = document.getElementById("updateFat");
    const updateCarbohydrates = document.getElementById("updateCarbohydrates");
    const updateFoodForm = document.getElementById("updateFoodForm");

    // ---------------------- Auto-fill Update Form ----------------------
    if (foodDropdown) {
        foodDropdown.addEventListener("change", function () {
            const selectedFood = foodDropdown.value;
            const selectedOption = foodDropdown.querySelector(`option[value="${selectedFood}"]`);
            if (selectedOption) {
                updateName.value = selectedOption.dataset.name;
                updateBrand.value = selectedOption.dataset.brand;
                updateServingSize.value = selectedOption.dataset.serving;
                updateCalories.value = selectedOption.dataset.calories;
                updateProtein.value = selectedOption.dataset.protein;
                updateFat.value = selectedOption.dataset.fat;
                updateCarbohydrates.value = selectedOption.dataset.carbs;
                updateFoodForm.action = `/update_food_item/${selectedFood}`;
            }
        });
    }

    // ---------------------- Edit Button ----------------------
    window.populateUpdateFoodForm = function (foodID) {
        foodDropdown.value = foodID;
        const selectedOption = foodDropdown.querySelector(`option[value="${foodID}"]`);
        if (selectedOption) {
            updateName.value = selectedOption.dataset.name;
            updateBrand.value = selectedOption.dataset.brand;
            updateServingSize.value = selectedOption.dataset.serving;
            updateCalories.value = selectedOption.dataset.calories;
            updateProtein.value = selectedOption.dataset.protein;
            updateFat.value = selectedOption.dataset.fat;
            updateCarbohydrates.value = selectedOption.dataset.carbs;
            updateFoodForm.action = `/update_food_item/${foodID}`;
        }
        updateFoodForm.scrollIntoView({ behavior: 'smooth' });
    };

    // ---------------------- Delete Food Item ----------------------
    window.deleteFoodItem = function (foodID) {
        if (confirm("Are you sure you want to delete this food item?")) {
            fetch(`/delete_food_item/${foodID}`, { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(`Food Item ${foodID} deleted successfully!`);
                        document.getElementById(`foodRow-${foodID}`).remove();
                        foodDropdown.querySelector(`option[value="${foodID}"]`).remove();
                        updateFoodForm.reset();
                        updateFoodForm.action = "";
                    }
                });
        }
    };
});
