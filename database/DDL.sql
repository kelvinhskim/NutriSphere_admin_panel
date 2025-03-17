-- -----------------------------------------------------
-- Project: NutriSphere: A Comprehensive Calorie Tracking System
-- Group 39
-- Emily Ho, Hyun Seok Kim
-- Data Definition Queries
-- This .SQL file is imported into Maria DB to create the tables aligning
-- with the defined schema from the project outline.
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Disable commits and foreign key checks to prevent issues during table creation.
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT = 0;


-- -----------------------------------------------------
-- Table `Users`
-- Stores user information including username, email, and default daily calorie goal.
-- Each user can log food entries and an exercise daily.
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `Users` (
  `userID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  `dailyCalorieGoal` INT NOT NULL CHECK (dailyCalorieGoal >= 0),
  PRIMARY KEY (`userID`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC)
);

-- -----------------------------------------------------
-- Table `Exercises`
-- Stores exercise information including name, duration, and calories burned.
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `Exercises` (
  `exerciseID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `exerciseMinutes` INT NOT NULL CHECK (exerciseMinutes >= 0),
  `caloriesBurned` INT NOT NULL CHECK (caloriesBurned >= 0),
  PRIMARY KEY (`exerciseID`)
);

-- -----------------------------------------------------
-- Table `DailyTrackers`
-- Stores the tracker date and user's calorie goal for that date.
-- Links to `Users`, `Exercises`, and `FoodItems` (thru `FoodEntries`) tables.
-- If a user is deleted, their records in `DailyTrackers` will be removed (ON DELETE CASCADE).
-- If an exercise is deleted, the reference in `DailyTrackers` is set to NULL (ON DELETE SET NULL).
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `DailyTrackers` (
  `dailyTrackerID` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `calorieGoal` INT CHECK (calorieGoal >= 0),
  `userID` INT NOT NULL,
  `exerciseID` INT DEFAULT NULL,
  PRIMARY KEY (`dailyTrackerID`),
  INDEX `fk_DailyTrackers_userID_idx` (`userID` ASC),
  INDEX `fk_DailyTrackers_exerciseID_idx` (`exerciseID` ASC),
  CONSTRAINT `tracker` UNIQUE (`userID`, `date`),
  CONSTRAINT `fk_DailyTrackers_userID`
    FOREIGN KEY (`userID`)
    REFERENCES `Users` (`userID`)
    ON DELETE CASCADE     -- If a user is deleted, remove all their trackers
    ON UPDATE CASCADE,    -- If a user's ID is updated, update it also on all associated trackers
  CONSTRAINT `fk_DailyTrackers_exerciseID`
    FOREIGN KEY (`exerciseID`)
    REFERENCES `Exercises` (`exerciseID`)
    ON DELETE SET NULL    -- If an exercise is deleted, dissociate it from all associated trackers
    ON UPDATE CASCADE     -- If an exercise ID is updated, update it also on all associated trackers
);

-- -----------------------------------------------------
-- Table `FoodItems`
-- Stores food items with nutrition information.
-- Includes calories, protein, fat, carbohydrates, and serving sizes.
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `FoodItems` (
  `foodItemID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `brand` VARCHAR(100) NULL,
  `servingSize` VARCHAR(45) NOT NULL,
  `calories` INT NOT NULL CHECK (calories >= 0),
  `protein` INT NULL CHECK (protein IS NULL OR protein >= 0),
  `fat` INT NULL CHECK (fat IS NULL OR fat >= 0),
  `carbohydrates` INT NULL CHECK (carbohydrates IS NULL OR carbohydrates >= 0),
  PRIMARY KEY (`foodItemID`)
);

-- -----------------------------------------------------
-- Table `FoodEntries` (Intersection table for M:N relationship between DailyTrackers and FoodItems)
-- Links DailyTrackers and FoodItems to track food consumption associated with users and their daily trackers.
-- If a food item is deleted, all associated food entries are removed (ON DELETE CASCADE).
-- If a daily tracker is deleted, all associated food entries are removed (ON DELETE CASCADE).
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `FoodEntries` (
  `foodEntryID` INT NOT NULL AUTO_INCREMENT,
  `mealCategory` ENUM('Breakfast', 'Lunch', 'Dinner', 'Snacks') NOT NULL,
  `foodItemID` INT NOT NULL,
  `dailyTrackerID` INT NOT NULL,
  PRIMARY KEY (`foodEntryID`),
  INDEX `fk_FoodEntries_foodItemID_idx` (`foodItemID` ASC),
  INDEX `fk_FoodEntries_dailyTrackerID_idx` (`dailyTrackerID` ASC),
  CONSTRAINT `fk_FoodEntries_foodItemID`
    FOREIGN KEY (`foodItemID`)
    REFERENCES `FoodItems` (`foodItemID`)
    ON DELETE CASCADE   -- If a food item is deleted, remove all associated food entries
    ON UPDATE CASCADE,  -- If a food item's ID is updated, update it also on all associated food entries
  CONSTRAINT `fk_FoodEntries_dailyTrackerID`
    FOREIGN KEY (`dailyTrackerID`)
    REFERENCES `DailyTrackers` (`dailyTrackerID`)
    ON DELETE CASCADE   -- If a tracker is deleted, remove all associated food entries
    ON UPDATE CASCADE   -- If a tracker's ID is updated, update it also on all associated food entries
);

-- -----------------------------------------------------
-- STORED PROCEDURE: `add_food_entry`
-- The stored procedure handles the case of when a food entry is attempting to be added for 
-- a specific user and date but the daily tracker for that user and date that has not been created yet.
-- If the appropriate daily tracker has not been created yet, create a new daily tracker for that user and date.
-- Then, for both scenarios (whether the tracker did not exist yet or already existed), insert the data into Food Entries.  
-- -----------------------------------------------------
DELIMITER $$
DROP PROCEDURE IF EXISTS `add_food_entry`;
CREATE PROCEDURE `add_food_entry`(IN pUserID INT, IN pDate DATE, IN pMealCategory VARCHAR(255), IN pFoodItemID INT)
BEGIN
    IF NOT EXISTS (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = pUserID AND date = pDate) THEN
        INSERT INTO DailyTrackers (date, calorieGoal, userID) VALUES (pDate, (SELECT dailyCalorieGoal FROM Users WHERE userID = pUserID), pUserID);
    END IF;
    INSERT INTO FoodEntries (mealCategory, foodItemID, dailyTrackerID) VALUES (pMealCategory, pFoodItemID, (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = pUserID AND date = pDate));
    END$$

DELIMITER ;


-- -----------------------------------------------------
-- Insert sample data for Users
-- -----------------------------------------------------
INSERT INTO `Users` (`username`, `email`, `dailyCalorieGoal`)
VALUES
('Tyler', 'tyler@gmail.com', 1800),
('Jane', 'jane@yahoo.com', 2100),
('Alex', 'alex@hotmail.com', 3000);

-- -----------------------------------------------------
-- Insert sample data for FoodItems
-- -----------------------------------------------------
INSERT INTO `FoodItems` (`name`, `brand`, `servingSize`, `calories`, `protein`, `fat`, `carbohydrates`)
VALUES
('Oatmeal', "Bob\'s Red Mill", '1 cup', 153, 5, 3, 27),
('Coffee', 'Starbucks', '1 cup (grande)', 15, 1, 0, 2),
('Salad', NULL, '1 bowl', 250, 8, 10, 30),
('Chicken', "Trader Joe\'s", '113g', 150, 27, 5, 0),
('Brown Rice', 'Nishiki', '210g', 340, 7, 3, 7),
('Big Mac', "McDonald\'s", '1 burger', 580, 25, 34, NULL);

-- -----------------------------------------------------
-- Insert sample data for Exercises
-- -----------------------------------------------------
INSERT INTO `Exercises` (`name`, `exerciseMinutes`, `caloriesBurned`)
VALUES
('Elliptical', 30, 250),
('Hiking', 120, 600),
('Swimming', 30, 300),
('Pickleball', 60, 400),
('Weight Lifting', 60, 150);

-- -----------------------------------------------------
-- Insert sample data for DailyTrackers (with SELECT subquery to populate FKs)
-- -----------------------------------------------------
INSERT INTO `DailyTrackers` (`date`, `calorieGoal`, `userID`, `exerciseID`)
VALUES
('2025-01-02', 2400, (SELECT userID FROM Users WHERE username = 'tyler'), (SELECT exerciseID FROM Exercises WHERE name = 'Elliptical')),
('2025-01-03', 2400, (SELECT userID FROM Users WHERE username = 'tyler'), (SELECT exerciseID FROM Exercises WHERE name IS NULL)),
('2025-01-20', 2000, (SELECT userID FROM Users WHERE username = 'jane'), (SELECT exerciseID FROM Exercises WHERE name = 'Pickleball')),
('2025-02-01', 2000, (SELECT userID FROM Users WHERE username = 'jane'), (SELECT exerciseID FROM Exercises WHERE name = 'Pickleball')),
('2025-02-04', 2200, (SELECT userID FROM Users WHERE username = 'alex'), (SELECT exerciseID FROM Exercises WHERE name = 'Weight Lifting'));

-- -----------------------------------------------------
-- Insert sample data for FoodEntries
-- -----------------------------------------------------
INSERT INTO `FoodEntries` (`mealCategory`, `foodItemID`, `dailyTrackerID`)
VALUES
('Breakfast', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Oatmeal' AND brand = "Bob\'s Red Mill"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-02')
),
('Lunch', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Coffee' AND brand = 'Starbucks'), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-02')
),
('Lunch', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Salad' AND brand IS NULL), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-02')
),
('Dinner', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Chicken' AND brand = "Trader Joe\'s"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-02')
),
('Lunch', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Big Mac' AND brand = "McDonald\'s"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-03')
),
('Dinner', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Salad' AND brand IS NULL), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-03')
),
('Dinner', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Chicken' AND brand = "Trader Joe\'s"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 1 AND date = '2025-01-03')
),
('Breakfast', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Coffee' AND brand = 'Starbucks'), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 2 AND date = '2025-01-20')
),
('Lunch', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Chicken' AND brand = "Trader Joe\'s"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 2 AND date = '2025-02-01')
),
('Dinner', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Big Mac' AND brand = "McDonald\'s"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 3 AND date = '2025-02-04')
),
('Breakfast', 
  (SELECT foodItemID FROM FoodItems WHERE name = 'Oatmeal' AND brand = "Bob\'s Red Mill"), 
  (SELECT dailyTrackerID FROM DailyTrackers WHERE userID = 2 AND date = '2025-01-20')
);

-- -----------------------------------------------------
-- Turn commits and foreign key checks back on.
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS=1;
COMMIT;
