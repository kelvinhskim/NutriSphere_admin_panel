-- -----------------------------------------------------
-- Project: NutriSphere: A Comprehensive Calorie Tracking System
-- Group 39
-- Group members: Emily Ho, Hyun Seok Kim
-- Data Manipulation Queries
-- -----------------------------------------------------

-- -----------------------------------------------------
-- PURPOSE:
-- This file contains Data Manipulation Language (DML) queries for CRUD operations.
-- These queries are used by the NutriSphere web application to interact with the database.
--
-- The queries cover:
--  1. Users Table (CRUD)
--  2. FoodItems Table (CRUD)
--  3. DailyTrackers Table (CRUD)
--  4. Exercises Table (CRUD)
--  5. FoodEntries Table (Many-to-Many CRUD)
--  6. Dynamic Dropdown Queries

-- NOTE:
-- In the queries below, variables that are preceded with a colon : character denote data that will be pulled from the Flask backend.
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Sources
-- -----------------------------------------------------
-- SQL Server CRUD Operations https://www.geeksforgeeks.org/sql-server-crud-operations/
-- bsg_sample_data_manipulation_queries.sql https://canvas.oregonstate.edu/courses/1987790/assignments/9888509?module_item_id=25023016
-- CS340 Project Guide https://canvas.oregonstate.edu/courses/1987790/pages/cs340-project-guide
-- Create-Read-Update-Delete (CRUD) functionalities https://en.wikipedia.org/wiki/Create,_read,_update_and_delete
-- SQL Server CONCAT() Function https://www.w3schools.com/sql/func_sqlserver_concat.asp
-- SQL Server COALESCE() Function https://www.w3schools.com/sql/func_sqlserver_coalesce.asp
-- ORDER BY CASE for custom sorting: https://www.geeksforgeeks.org/how-to-custom-sort-in-sql-order-by-clause/
-- MySQL Transactions: https://www.geeksforgeeks.org/mysql-transaction/
-- MySQL user-defined variables https://www.geeksforgeeks.org/mysql-user-defined-variables/
-- MySQL stored procedure https://www.mysqltutorial.org/mysql-stored-procedure/stored-procedures-parameters-in-mysql/
-- -----------------------------------------------------


-- -----------------------------------------------------
-- QUERIES FOR POPULATING DROPDOWNS (FOR FOREIGN KEY SELECTION)
-- -----------------------------------------------------

-- Retrieves all User IDs and Usernames to populate the Username dropdown
SELECT userID, username FROM Users ORDER BY username;

-- Retrieves all Food IDs and Names for dropdown selection
SELECT foodItemID, CONCAT(name, ' (', brand, ')') AS food_display FROM FoodItems ORDER BY name;

-- Retrieves all Exercise IDs and Names to populate the Exercise dropdown
SELECT exerciseID, name FROM Exercises ORDER BY name;

-- Retrieves all Daily Tracker IDs, Dates, and Usernames of daily tracker entries for dropdown selection
SELECT dailyTrackerID, CONCAT(date, ' - ', username) AS tracker_display
FROM DailyTrackers
JOIN Users ON DailyTrackers.userID = Users.userID
ORDER BY Users.username DESC, date DESC;


-- -----------------------------------------------------
-- USERS Page - CRUD OPERATIONS
-- -----------------------------------------------------

-- READ: Retrieves all users from the database to display in the user management page
SELECT userID, username, email, dailyCalorieGoal
FROM Users
ORDER BY username;

-- CREATE: Adds a new user into the Users table
INSERT INTO Users (username, email, dailyCalorieGoal)
VALUES (:usernameInput, :emailInput, :dailyCalorieGoalInput);

-- UPDATE: Updates the email and/or daily calorie goal of the selected user based on the user ID provided from the frontend
-- gets a single user's data for the Update User Form
SELECT userID, email, dailyCalorieGoal FROM Users WHERE userID = :userID_selected_from_users_page;
-- updates a user's data based on submission of the Update User Form
UPDATE Users
SET email = :emailInput, dailyCalorieGoal = :dailyCalorieGoalInput
WHERE userID = :userID_selected_from_update_form;

-- DELETE: Deletes a user from the Users table, automatically removing related DailyTrackers due to ON DELETE CASCADE
DELETE FROM Users WHERE userID = :userID_selected_from_users_page;


-- -----------------------------------------------------
-- FOOD Library Page - CRUD OPERATIONS
-- -----------------------------------------------------

-- READ: Retrieves all food items and their corresponding details to populate the Food Library page
SELECT foodItemID, name, brand, servingSize, calories, protein, fat, carbohydrates
FROM FoodItems
ORDER BY name;

-- CREATE: Adds a new food item into the FoodItems table
INSERT INTO FoodItems (name, brand, servingSize, calories, protein, fat, carbohydrates)
VALUES (:nameInput, :brandInput, :servingSizeInput, :caloriesInput, :proteinInput, :fatInput, :carbohydratesInput);

-- UPDATE: Updates the details of a food item (name, brand, calories, etc) based on the foodItemID selected from the Food Library page
-- gets a single food item's data for the Update Food Item form
SELECT name, brand, servingSize, calories, protein, fat, carbohydrates FROM FoodItems WHERE foodItemID = :foodItemID_selected_from_food_library_page;
-- updates a food item's data based on submission of the Update Food Item form
UPDATE FoodItems
SET name = :nameInput, brand = :brandInput, servingSize = :servingSizeInput, calories = :caloriesInput, protein = :proteinInput, fat = :fatInput, carbohydrates = :carbohydratesInput
WHERE foodItemID = :foodItemID_selected_from_update_form;

-- DELETE: Deletes a food item from the database, ensuring referential integrity in the FoodEntries table
DELETE FROM FoodItems WHERE foodItemID = :foodItemID_selected_from_food_library_page;


-- -----------------------------------------------------
-- DAILY TRACKERS Page - CRUD OPERATIONS
-- -----------------------------------------------------

-- READ: Retrieves all daily tracker entries along with associated users and exercises
SELECT dt.dailyTrackerID, dt.date, u.username, u.dailyCalorieGoal, dt.caloriesConsumed, e.caloriesBurned, dt.caloriesRemaining,
       COALESCE(e.name, 'No Exercise Logged') AS exercise
FROM DailyTrackers AS dt
LEFT JOIN Users AS u ON dt.userID = u.userID
LEFT JOIN Exercises AS e ON dt.exerciseID = e.exerciseID
ORDER BY dt.date DESC;

-- CREATE: Adds a new daily tracker entry for a user
INSERT INTO DailyTrackers (date, userID, exerciseID)
VALUES (:dateInput, :userID_from_dropdown_Input, :exerciseID_from_dropdown_Input);

-- UPDATE: Updates a specific daily tracker entry based on submission of the Update Daily Tracker Entry form
UPDATE DailyTrackers
SET date = :dateInput, userID = :userID_from_dropdown_Input, exerciseID = :exerciseID_from_dropdown_Input
WHERE dailyTrackerID = :dailyTrackerID_from_update_form;

-- DELETE: Deletes a daily tracker entry; associated food entries are removed due to ON DELETE CASCADE
DELETE FROM DailyTrackers WHERE dailyTrackerID = :dailyTrackerID_selected_from_daily_trackers_page;


-- -----------------------------------------------------
-- EXERCISE Library Page - CRUD OPERATIONS
-- -----------------------------------------------------

-- READ: Retrieves all exercises for the Exercise Library page
SELECT exerciseID, name, exerciseMinutes, caloriesBurned
FROM Exercises
ORDER BY name;

-- CREATE: Adds a new exercise to the Exercise Library
INSERT INTO Exercises (name, exerciseMinutes, caloriesBurned)
VALUES (:nameInput, :exerciseMinutesInput, :caloriesBurnedInput);

-- UPDATE: Updates the details of an exercise (name, duration, or calories burned) based on submission of the Update Exercise form
UPDATE Exercises
SET name = :nameInput, exerciseMinutes = :exerciseMinutesInput, caloriesBurned = :caloriesBurnedInput
WHERE exerciseID = :exerciseID_selected_from_exercise_library_page;

-- DELETE: Deletes an exercise from the Exercises table and sets related exerciseID of daily tracker entries to NULL
DELETE FROM Exercises WHERE exerciseID = :exerciseID_selected_from_exercise_library_page;


-- -----------------------------------------------------
--  FOOD ENTRIES (M:N Relationship) - CRUD OPERATIONS
-- -----------------------------------------------------

-- Create a stored procedure to update the total calories consumed by a user on a specified date (in the Daily Trackers table)
DELIMITER //
CREATE PROCEDURE UpdateTotalCaloriesConsumed(IN dailyTrackerID INT)
BEGIN
       SET @updatedCalories = (
              SELECT SUM(fi.calories FROM FoodEntries AS fe
              LEFT JOIN FoodItems AS fi ON fe.foodItemID = fi.foodItemID
              WHERE fe.dailyTrackerID = @dailyTrackerID)
       )
       WHERE dailyTrackerID = @dailyTrackerID
END
DELIMITER ;

-- READ: Retrieves all food entries associated with users' daily trackers
SELECT fe.foodEntryID, dt.date, u.username, fe.mealCategory, fi.name AS food, fi.calories, dt.dailyTrackerID
FROM FoodEntries AS fe
JOIN DailyTrackers AS dt ON fe.dailyTrackerID = dt.dailyTrackerID
JOIN Users AS u ON dt.userID = u.userID
JOIN FoodItems AS fi ON fe.foodItemID = fi.foodItemID
ORDER BY dt.date DESC, u.username ASC,
       CASE
       WHEN fe.mealCategory = 'Breakfast' then 1,
       WHEN fe.mealCategory = 'Lunch' then 2,
       WHEN fe.mealCategory = 'Dinner' then 3,
       WHEN fe.mealCategory = 'Snacks' then 4
       END ASC;

-- CREATE: Adds a new food entry in a specific user's daily tracker for a specific date
START TRANSACTION;
       -- if a daily tracker does not yet exist with the selected username and date, then create a new daily tracker with that selected username and date
       INSERT INTO DailyTrackers (userID, date)
       SELECT :userID_from_dropdown_Input, :date_from_dropdown_Input
       WHERE NOT EXISTS (SELECT 1 FROM DailyTrackers WHERE userID = :userID_from_dropdown_Input AND date = :date_from_dropdown_Input);
       -- then sets a variable to save the daily tracker ID associated with the selected username and date
       SET @specifiedDailyTrackerID = (SELECT dailyTrackerID FROM DailyTrackers
       WHERE userID = :userID_from_dropdown_Input AND date = :date_from_dropdown_Input);
       -- then add a new food entry linked to the dailyTrackerID (associated with the username and date)
       INSERT INTO FoodEntries (mealCategory, foodItemID, dailyTrackerID)
       VALUES (
              :mealCategory_from_dropdown_Input,
              :foodItemID_from_dropdown_Input,
              @specifiedDailyTrackerID
       );
       -- then updates total amount of calories consumed in Daily Trackers table
       UPDATE DailyTrackers
       SET caloriesConsumed = (
              SELECT SUM(fi.calories FROM FoodEntries AS fe
              LEFT JOIN FoodItems AS fi ON fe.foodItemID = fi.foodItemID
              WHERE fe.dailyTrackerID = @specifiedDailyTrackerID)
       )
       WHERE dailyTrackerID = @specifiedDailyTrackerID;
COMMIT;

-- UPDATE: Updates a food entry based on submission of the Update Food Entry form
UPDATE FoodEntries
SET mealCategory = :mealCategory_from_dropdown_Input, foodItemID = :foodItemID_from_dropdown_Input,
WHERE foodEntryID = :foodEntryID_selected_from_food_entries_page;
-- updates total calories consumed in DailyTrackers table using a stored procedure
CALL UpdateTotalCaloriesConsumed(:dailyTrackerID_from_update_form);

-- DELETE: Disassociates a food item from a user's daily tracker (M:N relationship deletion) and updates total calories consumed on DailyTrackers
START TRANSACTION;
       -- sets a variable to save the associated daily tracker ID
       SET @specifiedDailyTrackerID = (SELECT dailyTrackerID FROM FoodEntries WHERE foodEntryID = :foodEntryID_selected_from_food_entries_page);
       -- deletes the food entry
       DELETE FROM FoodEntries WHERE foodEntryID = :foodEntryID_selected_from_food_entries_page;
       -- updates total calories consumed in DailyTrackers table using a stored procedure
       CALL UpdateTotalCaloriesConsumed(@specifiedDailyTrackerID);
COMMIT;
