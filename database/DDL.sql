-- -----------------------------------------------------
-- Project: NutriSphere: A Comprehensive Calorie Tracking System
-- Group 39
-- Emily Ho, Hyun Seok Kim
-- Data Definition Queries
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Disable commits and foreign key checks to prevent issues during table creation.
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT = 0;


-- -----------------------------------------------------
-- Table `Users`
-- Stores user information including username, email, and daily calorie goal.
-- Each user can log food entries and exercises daily.
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `Users` (
  `userID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  `dailyCalorieGoal` INT NOT NULL CHECK (dailyCalorieGoal > 0),
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
-- Stores users' daily calorie intake and exercises performed
-- Links to `Users` and `Exercises` tables.
-- If a user is deleted, their records in `DailyTrackers` will be removed (ON DELETE CASCADE).
-- If an exercise is deleted, the reference in `DailyTrackers` is set to NULL (ON DELETE SET NULL).
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `DailyTrackers` (
  `dailyTrackerID` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `calorieGoal` INT,
  `caloriesConsumed` INT NOT NULL DEFAULT 0 CHECK (caloriesConsumed >= 0),
  `caloriesRemaining` INT NULL CHECK (caloriesRemaining >= 0),
  `userID` INT NOT NULL,
  `exerciseID` INT DEFAULT NULL,
  PRIMARY KEY (`dailyTrackerID`),
  INDEX `fk_DailyTrackers_userID_idx` (`userID` ASC),
  INDEX `fk_DailyTrackers_exerciseID_idx` (`exerciseID` ASC),
  CONSTRAINT `fk_DailyTrackers_userID`
    FOREIGN KEY (`userID`)
    REFERENCES `Users` (`userID`)
    ON DELETE CASCADE     -- If a user is deleted, remove all their trackers
    ON UPDATE CASCADE,    -- If a user's ID is updated, update the tracker's ID
  CONSTRAINT `fk_DailyTrackers_exerciseID`
    FOREIGN KEY (`exerciseID`)
    REFERENCES `Exercises` (`exerciseID`)
    ON DELETE SET NULL    -- If an exercise is deleted, dissociate it from the tracker
);

-- -----------------------------------------------------
-- Table `FoodItems`
-- Stores food items with nutriiton information.
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
-- Table `FoodEntries` (M:N Relationship)
-- Links DailyTrackers and FoodItems to track food consumption.
-- If a food item is deleted, remove all associated entries (ON DELETE CASCADE).
-- If a daily tracker is deleted, dissociate its entries (ON DELETE SET NULL).
-- -----------------------------------------------------
CREATE OR REPLACE TABLE `FoodEntries` (
  `foodEntryID` INT NOT NULL AUTO_INCREMENT,
  `mealCategory` ENUM('Breakfast', 'Lunch', 'Dinner', 'Snacks') NOT NULL,
  `foodItemID` INT,
  `dailyTrackerID` INT,
  PRIMARY KEY (`foodEntryID`),
  INDEX `fk_FoodEntries_foodItemID_idx` (`foodItemID` ASC),
  INDEX `fk_FoodEntries_dailyTrackerID_idx` (`dailyTrackerID` ASC),
  CONSTRAINT `fk_FoodEntries_foodItemID`
    FOREIGN KEY (`foodItemID`)
    REFERENCES `FoodItems` (`foodItemID`)
    ON DELETE CASCADE   -- If a food item is deleted, remove all entries
    ON UPDATE CASCADE,  -- If a food item's ID is updated, update the entries
  CONSTRAINT `fk_FoodEntries_dailyTrackerID`
    FOREIGN KEY (`dailyTrackerID`)
    REFERENCES `DailyTrackers` (`dailyTrackerID`)
    ON DELETE SET NULL   -- If a tracker is deleted, keep FoodEntries but set dailyTrackerID to NULL
    ON UPDATE CASCADE   -- If a tracker's ID is updated, update the entries
);

-- -----------------------------------------------------
-- TRIGGER: Auto-update 'caloriesConsumed when a new FoodEntry is inserted.
-- Automatically updates `caloriesConsumed` in `DailyTrackers`
-- whenever a new food entry is added.
-- Ensures that food consumption tracking remains accurate.
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
-- Automatically updates `caloriesRemaining` in `DailyTrackers`
-- whenever `caloriesConsumed` or `exerciseID` changes.
-- Ensures that calorie goals remain accurate.
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
INSERT INTO `Users` (`username`, `email`, `dailyCalorieGoal`)
VALUES
('tyler', 'tyler@gmail.com', 2400),
('jane', 'jane@yahoo.com', 2000),
('alex', 'alex@hotmail.com', 2200);

-- -----------------------------------------------------
-- Insert sample data for FoodItems
-- -----------------------------------------------------
INSERT INTO `FoodItems` (`name`, `brand`, `servingSize`, `calories`, `protein`, `fat`, `carbohydrates`)
VALUES
('Oatmeal', "Bob\'s Red Mill", '1 cup', 153, 5, 3, 27),
('Coffee', 'Starbucks', '1 cup (grande)', 15, 1, 0, 2),
('Salad', NULL, '1 bowl', 250, 8, 10, 30),
('Chicken ', "Trader Joe\'s", '113g', 150, 27, 5, 0),
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
-- Insert sample data for DailyTrackers
-- -----------------------------------------------------
INSERT INTO `DailyTrackers` (`date`, `calorieGoal`, `caloriesConsumed`, `caloriesRemaining`, `userID`, `exerciseID`)
VALUES
('2025-01-02', 2400, 0, NULL, 1, 1),
('2025-01-03', 2400, 0, NULL, 1, NULL),
('2025-01-20', 2000, 0, NULL, 2, 4),
('2025-02-01', 2000, 0, NULL, 2, 4),
('2025-02-04', 2200, 0, NULL, 3, 5);

-- -----------------------------------------------------
-- Insert sample data for FoodEntries
-- -----------------------------------------------------
INSERT INTO `FoodEntries` (`mealCategory`, `foodItemID`, `dailyTrackerID`)
VALUES
('Breakfast', 1, 1),
('Lunch', 2, 1),
('Lunch', 3, 1),
('Dinner', 4, 1),
('Lunch', 6, 2),
('Dinner', 3, 2),
('Dinner', 4, 2),
('Breakfast', 2, 3),
('Lunch', 4, 4),
('Dinner', 6, 5),
('Breakfast', 1, 3);

-- -----------------------------------------------------
-- Turn commits and foreign key checks back on.
-- -----------------------------------------------------
SET FOREIGN_KEY_CHECKS=1;
COMMIT;
