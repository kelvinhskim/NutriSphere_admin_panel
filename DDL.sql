-- -----------------------------------------------------
-- CS 340: Group 39 Project Step 2
-- Data Definition Queries
-- -----------------------------------------------------


-- Disable commits and foreign key checks to prevent issues during table creation.
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT = 0;


-- -----------------------------------------------------
-- Table `Users`
-- Stores user information including username, email, and daily calorie goal.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Users` (
  `userID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  `dailyCalorieGoal` INT NOT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC)
);

-- -----------------------------------------------------
-- Table `Exercises`
-- Stores exercise information including name, duration, and calories burned.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Exercises` (
  `exerciseID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `exerciseMinutes` INT NOT NULL,
  `caloriesBurned` INT NOT NULL,
  PRIMARY KEY (`exerciseID`)
);

-- -----------------------------------------------------
-- Table `DailyTrackers`
-- Stores users' daily calorie intake and exercises performed
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `DailyTrackers` (
  `dailyTrackerID` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `caloriesConsumed` INT NOT NULL DEFAULT 0,
  `caloriesRemaining` INT NULL,
  `userID` INT NOT NULL,
  `exerciseID` INT NULL,
  PRIMARY KEY (`dailyTrackerID`),
  INDEX `fk_DailyTrackers_Users1_idx` (`userID` ASC),
  INDEX `fk_DailyTrackers_Exercises1_idx` (`exerciseID` ASC),
  CONSTRAINT `fk_DailyTrackers_Users1`
    FOREIGN KEY (`userID`)
    REFERENCES `Users` (`userID`)
    ON DELETE CASCADE     -- If a user is deleted, remove all their trackers                  
    ON UPDATE CASCADE,    -- If a user's ID is updated, update the tracker's ID
  CONSTRAINT `fk_DailyTrackers_Exercises1`
    FOREIGN KEY (`exerciseID`)
    REFERENCES `Exercises` (`exerciseID`)
    ON DELETE SET NULL    -- If an exercise is deleted, set the tracker's exercise to NULL  
    ON UPDATE CASCADE     -- If an exercise's ID is updated, update the tracker's exercise ID
);

-- -----------------------------------------------------
-- Table `FoodItems`
-- Stores food items with nurtiriton information.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `FoodItems` (
  `foodItemID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `brand` VARCHAR(100) NULL,
  `servingSize` VARCHAR(45) NOT NULL,
  `calories` INT NOT NULL,
  `protein` INT NULL,
  `fat` INT NULL,
  `carbohydrates` INT NULL,
  PRIMARY KEY (`foodItemID`)
);

-- -----------------------------------------------------
-- Table `FoodEntries` (M:N Relationship)
-- Links DailyTrackers and FoodItems to track food consumption.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `FoodEntries` (
  `foodEntryID` INT NOT NULL AUTO_INCREMENT,
  `mealCategory` ENUM('Breakfast', 'Lunch', 'Dinner', 'Snacks') NOT NULL,
  `foodItemID` INT NOT NULL,
  `dailyTrackerID` INT NOT NULL,
  PRIMARY KEY (`foodEntryID`),
  INDEX `fk_FoodEntries_FoodItems1_idx` (`foodItemID` ASC),
  INDEX `fk_FoodEntries_DailyTrackers1_idx` (`dailyTrackerID` ASC),
  CONSTRAINT `fk_foodEntries_food`
    FOREIGN KEY (`foodItemID`)
    REFERENCES `FoodItems` (`foodItemID`)
    ON DELETE CASCADE   -- If a food item is deleted, remove all entries
    ON UPDATE CASCADE,  -- If a food item's ID is updated, update the entries
  CONSTRAINT `fk_foodEntries_dailyTracker1`
    FOREIGN KEY (`dailyTrackerID`)
    REFERENCES `DailyTrackers` (`dailyTrackerID`)
    ON DELETE CASCADE   -- If a tracker is deleted, remove all entries
    ON UPDATE CASCADE   -- If a tracker's ID is updated, update the entries
);

-- -----------------------------------------------------
-- TRIGGER: Auto-update 'caloriesConsumed when a new FoodEntry is inserted.
-- -----------------------------------------------------
DELIMITER $$

CREATE TRIGGER update_calories_consumed
AFTER INSERT ON FoodEntries
FOR EACH ROW
BEGIN
    UPDATE DailyTrackers
    SET caloriesConsumed = (
        SELECT COALESCE(SUM(FI.calories), 0) 
        FROM FoodEntries FE
        JOIN FoodItems FI ON FE.foodItemID = FI.foodItemID
        WHERE FE.dailyTrackerID = NEW.dailyTrackerID
    )
    WHERE dailyTrackerID = NEW.dailyTrackerID;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- TRIGGER: Auto-update 'caloriesRemaining' when 'caloriesConsumed' or 'exerciseID' changes.
-- -----------------------------------------------------
DELIMITER $$

CREATE TRIGGER update_calories_remaining
BEFORE UPDATE ON DailyTrackers
FOR EACH ROW
BEGIN
    DECLARE goal INT;
    DECLARE burned INT;

     -- Get the user's daily calorie goal
    SELECT dailyCalorieGoal INTO goal FROM Users WHERE userID = NEW.userID;

    -- Get the total calories burned (if an exercise is logged)
    SELECT COALESCE((SELECT caloriesBurned FROM Exercises WHERE exerciseID = NEW.exerciseID), 0) INTO burned;

    -- Calculate new caloriesRemaining
    SET NEW.caloriesRemaining = goal - NEW.caloriesConsumed + burned;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- Insert sample data for Users
-- -----------------------------------------------------
INSERT INTO `Users` (`userID`, `username`, `email`, `dailyCalorieGoal`) 
VALUES
(1, 'Tyler', 'tyler@oregonstate.edu', 2400),
(2, 'Jane', 'jane@oregonstate.edu', 2000),
(3, 'Alex', 'alex@oregonstate.edu', 2200);

-- -----------------------------------------------------
-- Insert sample data for FoodItems
-- -----------------------------------------------------
INSERT INTO `FoodItems` (`foodItemID`, `name`, `brand`, `servingSize`, `calories`, `protein`, `fat`, `carbohydrates`) 
VALUES
(1, 'Oatmeal', "Bob\'s Red Mill", '1 cup', 153, 5, 3, 27),
(2, 'Coffee', 'Starbucks', '1 cup (grande)', 15, 1, 0, 2),
(3, 'Salad', 'Organic', '1 bowl', 250, 8, 10, 30),
(4, 'Chicken ', "Trader Joe\'s", '113g', 150, 27, 5, 0),
(5, 'Brown Rice', 'Nishiki', '210g', 340, 7, 3, 7),
(6, 'Big Mac', "McDonald\'s", '1 burger', 580, 25, 34, NULL);

-- -----------------------------------------------------
-- Insert sample data for Exercises
-- -----------------------------------------------------
INSERT INTO `Exercises` (`exerciseID`, `name`, `exerciseMinutes`, `caloriesBurned`) 
VALUES
(1, 'Elliptical', 30, 250),
(2, 'Hiking', 120, 600),
(3, 'Swimming', 30, 300),
(4, 'Pickleball', 60, 400),
(5, 'Weight Lifting', 60, 150);

-- -----------------------------------------------------
-- Insert sample data for DailyTrackers
-- -----------------------------------------------------
INSERT INTO `DailyTrackers` (`dailyTrackerID`, `date`, `caloriesConsumed`, `caloriesRemaining`, `userID`, `exerciseID`) 
VALUES
(1, '2025-01-02', 0, NULL, 1, 1),
(2, '2025-01-03', 0, NULL, 1, NULL),
(3, '2025-01-20', 0, NULL, 2, 4),
(4, '2025-02-01', 0, NULL, 2, 4),
(5, '2025-02-04', 0, NULL, 3, 5);

-- -----------------------------------------------------
-- Insert sample data for FoodEntries
-- -----------------------------------------------------
INSERT INTO `FoodEntries` (`foodEntryID`, `mealCategory`, `foodItemID`, `dailyTrackerID`) 
VALUES
(1, 'Breakfast', 1, 1),
(2, 'Lunch', 2, 1),
(3, 'Lunch', 3, 1),
(4, 'Dinner', 4, 1),
(5, 'Lunch', 6, 2),
(6, 'Dinner', 3, 2),
(7, 'Dinner', 4, 2),
(8, 'Breakfast', 2, 3),
(9, 'Lunch', 4, 4),
(10, 'Dinner', 6, 5),
(11, 'Breakfast', 1, 3);

-- -----------------------------------------------------
-- Turn commits and foreign key checks back on.
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS=1;
COMMIT;