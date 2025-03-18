-- -----------------------------------------------------
-- Project: NutriSphere: A Comprehensive Calorie Tracking System
-- Group 39
-- Group members: Emily Ho, Hyun Seok Kim
-- Data Manipulation Queries
-- -----------------------------------------------------

-- Citation for DML queries
-- Date: 2/13/25
-- Adapted from example on Canvas
-- Source URL: https://canvas.oregonstate.edu/courses/1987790/files/108859857?wrap=1 

-- -----------------------------------------------------
-- PURPOSE:
-- This file contains Data Manipulation Language (DML) queries for CRUD operations.
-- These queries are used by the frontend UI to interact with the NutriSphere database.
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
SELECT userID, username, dailyCalorieGoal FROM Users ORDER BY username;

-- Retrieves all Food IDs and Names for dropdown selection
SELECT foodItemID, CONCAT(name, ' (', brand, ')') AS food_display FROM FoodItems ORDER BY name;

-- Retrieves all Exercise IDs and Names to populate the Exercise dropdown
SELECT exerciseID, name FROM Exercises ORDER BY name;

-- Retrieves all Daily Tracker IDs, Dates, and Usernames of daily tracker entries for dropdown selection
SELECT dt.dailyTrackerID, u.username, dt.date 
FROM DailyTrackers dt
JOIN Users u ON dt.userID = u.userID
ORDER BY dt.date DESC, u.username DESC;

-- Retrieves all Food Items
SELECT foodItemID, name, brand FROM FoodItems;


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
-- FOOD ITEMS Page - CRUD OPERATIONS
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

-- READ: Retrieves all daily trackers along with associated users and exercises. 
-- Also calculates calories consumed, calories burned, and calories remaining.
SELECT 
       dt.dailyTrackerID AS `Daily Tracker ID`, 
       u.username AS `Username`, 
       dt.date AS `Date`, 
       dt.calorieGoal AS `Calorie Goal`, 
       (SELECT IFNULL(SUM(fi.calories), 0)
       FROM FoodEntries fe
       LEFT JOIN FoodItems fi ON fe.foodItemID = fi.foodItemID
       WHERE fe.dailyTrackerID = dt.dailyTrackerID) AS `Calories Consumed`,
       IFNULL(e.caloriesBurned, 0) AS `Calories Burned`, 
       (dt.calorieGoal - (SELECT IFNULL(SUM(fi.calories), 0)
       FROM FoodEntries fe
       LEFT JOIN FoodItems fi ON fe.foodItemID = fi.foodItemID
       WHERE fe.dailyTrackerID = dt.dailyTrackerID) 
       + IFNULL(e.caloriesBurned, 0)) AS `Calories Remaining`, 
       IFNULL(e.name, 'No Exercise Logged') AS `Exercise Logged` 
FROM DailyTrackers dt 
LEFT JOIN Users u ON dt.userID = u.userID 
LEFT JOIN Exercises e ON dt.exerciseID = e.exerciseID 
ORDER BY dt.date DESC, u.username ASC;

-- CREATE: Adds a new daily tracker for a user on a specified date.
INSERT INTO DailyTrackers (date, calorieGoal, userID, exerciseID)
VALUES (:date_Input, :calorieGoal_Input, :userID_from_dropdown_Input, :exerciseID_from_dropdown_Input);

-- UPDATE: Updates a selected daily tracker when the Update Daily Tracker form is submitted.
-- Updates the user, date, calorie goal and/or exercise on a selected daily tracker.
UPDATE DailyTrackers
SET date = :date_Input, calorieGoal = :calorieGoal_Input, userID = userID_from_dropdown_Input, exerciseID = :exerciseID_from_dropdown_Input
WHERE dailyTrackerID = :dailyTrackerID_from_update_form;

-- DELETE: Deletes a selected daily tracker. 
-- Associated food entries are removed due to ON DELETE CASCADE.
DELETE FROM DailyTrackers WHERE dailyTrackerID = :dailyTrackerID_selected_from_daily_trackers_page;


-- -----------------------------------------------------
-- EXERCISES Page - CRUD OPERATIONS
-- -----------------------------------------------------

-- READ: Retrieves all exercises for the Exercises page
SELECT exerciseID, name, exerciseMinutes, caloriesBurned
FROM Exercises
ORDER BY name;

-- CREATE: Adds a new exercise to the Exercises list
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

-- READ: Retrieves all food entries, which are associated with users' daily trackers and food items.
SELECT 
       fe.foodEntryID AS `Food Entry ID`, 
       fe.mealCategory AS `Meal Category`,
       CASE
       WHEN fi.brand IS NULL THEN fi.name
       ELSE CONCAT(fi.name, ', ', IFNULL(fi.brand, '')) 
       END AS `Food`, 
       fi.calories AS `Calories`, 
       CONCAT(dt.dailyTrackerID, ': ', u.username, ', ', dt.date) AS `Daily Tracker` 
FROM FoodEntries AS fe 
JOIN DailyTrackers AS dt ON fe.dailyTrackerID = dt.dailyTrackerID 
JOIN Users AS u ON dt.userID = u.userID 
JOIN FoodItems AS fi ON fe.foodItemID = fi.foodItemID 
ORDER BY dt.date DESC, u.username ASC, 
       CASE 
       WHEN fe.mealCategory = 'Breakfast' then 1 
       WHEN fe.mealCategory = 'Lunch' then 2 
       WHEN fe.mealCategory = 'Dinner' then 3 
       WHEN fe.mealCategory = 'Snacks' then 4 
       END ASC;

-- CREATE: Adds a new food entry in a specific user's daily tracker for a specific date.
-- Make a call to the stored procedure add_food_entry. It handles the case of when a food entry is attempting to be added for 
-- a specific user and date but the daily tracker for that user and date that has not been created yet.
-- // The following add_food_entry stored procedure is placed in the DDL.sql file.
-- DELIMITER $$
-- DROP PROCEDURE IF EXISTS `add_food_entry`;
-- CREATE PROCEDURE `add_food_entry`(IN pUserID INT, IN pDate DATE, IN pMealCategory VARCHAR(255), IN pFoodItemID INT)
-- BEGIN
--     IF NOT EXISTS (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = pUserID AND date = pDate) THEN
--         INSERT INTO DailyTrackers (date, calorieGoal, userID) VALUES (pDate, (SELECT dailyCalorieGoal FROM Users WHERE userID = pUserID), pUserID);
--     END IF;
--     INSERT INTO FoodEntries (mealCategory, foodItemID, dailyTrackerID) VALUES (pMealCategory, pFoodItemID, (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = pUserID AND date = pDate));
--     END$$
-- DELIMITER ;
-- // 
CALL add_food_entry(userID_from_dropdown_Input, date_Input, mealCategory_from_dropdown_Input, foodItemID_from_dropdown_Input)

-- UPDATE: Updates a food entry based on submission of the Update Food Entry form
UPDATE FoodEntries
SET mealCategory = :mealCategory_from_dropdown_Input, foodItemID = :foodItemID_from_dropdown_Input,
WHERE foodEntryID = :foodEntryID_selected_from_food_entries_page;

-- DELETE: Disassociates a food item from a user's daily tracker (M:N relationship deletion).
DELETE FROM FoodEntries WHERE foodEntryID = :foodEntryID_selected_from_food_entries_page;
