-- START of Problem 1 Solution --
# create the table
DROP DATABASE IF EXISTS `roomsync`;
CREATE DATABASE IF NOT EXISTS `roomsync`;
USE `roomsync`;


# create the users table
CREATE TABLE Users (
   userID      INT AUTO_INCREMENT NOT NULL,
   userName    VARCHAR(50)  UNIQUE NOT NULL,
   userEmail   VARCHAR(100) UNIQUE NOT NULL,
   userPhone   VARCHAR(20),
   userRole    VARCHAR(50)  NOT NULL,
   userStatus  VARCHAR(50)  NOT NULL DEFAULT 'active',
   PRIMARY KEY (userID)
);


CREATE TABLE Neighborhood (
   neighborhoodID          INT AUTO_INCREMENT,
   neighborhoodName        VARCHAR(50) NOT NULL,
   neighborhoodInsights    TEXT,
   PRIMARY KEY (neighborhoodID)
);


# create the apartment table
CREATE TABLE Apartment (
   apartmentID       INT AUTO_INCREMENT,
   unitNumber        VARCHAR(20) NOT NULL,
   neighborhoodID    INT NOT NULL,
   PRIMARY KEY(apartmentID),
   FOREIGN KEY (neighborhoodID) REFERENCES Neighborhood(neighborhoodID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


# create the apartment features table
CREATE TABLE ApartmentFeatures (
   featureID   INT AUTO_INCREMENT,
   value       VARCHAR(100) NOT NULL,
   label       VARCHAR(100) NOT NULL,
   PRIMARY KEY(featureID)
);


CREATE TABLE Admin (
   adminID     INT AUTO_INCREMENT,
   userID      INT NOT NULL,
   adminName   VARCHAR(100) NOT NULL,
   adminEmail  VARCHAR(100) NOT NULL,
   roleTitle   VARCHAR(50),
   PRIMARY KEY(adminID),
   FOREIGN KEY (userID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE Renter (
   renterID    INT AUTO_INCREMENT PRIMARY KEY,
   userID      INT NOT NULL,
   firstName   VARCHAR(50)  NOT NULL,
   lastName    VARCHAR(50)  NOT NULL,
   email       VARCHAR(100),
   phoneNumber VARCHAR(20),
   schoolName  VARCHAR(100),
   income      DECIMAL(10,2),
   FOREIGN KEY (userID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);




CREATE TABLE Landlord (
   landlordID  INT AUTO_INCREMENT PRIMARY KEY,
   userID      INT NOT NULL,
   firstName   VARCHAR(50)  NOT NULL,
   lastName    VARCHAR(50)  NOT NULL,
   email       VARCHAR(100) NOT NULL,
   phone       VARCHAR(20),
   isVerified  BOOLEAN      NOT NULL DEFAULT FALSE,
   joinedDate  DATE         NOT NULL DEFAULT (CURRENT_DATE),
   FOREIGN KEY (userID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);




CREATE TABLE Broker (
   brokerID    INT AUTO_INCREMENT,
   userID      INT NOT NULL,
   brokerName  VARCHAR(100) NOT NULL,
   brokerPhone VARCHAR(20),
   brokerEmail VARCHAR(100),
   PRIMARY KEY(brokerID),
   FOREIGN KEY (userID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);




CREATE TABLE RenterPreferences (
   renterID    INT NOT NULL,
   featureID   INT NOT NULL,
   PRIMARY KEY (renterID, featureID),
   FOREIGN KEY (renterID)  REFERENCES Renter(renterID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (featureID) REFERENCES ApartmentFeatures(featureID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE Dealbreakers (
   renterID    INT NOT NULL,
   featureID   INT NOT NULL,
   PRIMARY KEY (renterID, featureID),
   FOREIGN KEY (renterID)  REFERENCES Renter(renterID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (featureID) REFERENCES ApartmentFeatures(featureID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE Listing (
   listingID       INT AUTO_INCREMENT PRIMARY KEY,
   apartmentID     INT NOT NULL,
   landlordID      INT NOT NULL,
   brokerID        INT,
   renterID        INT,
   availableDate   DATE         NOT NULL,
   status          VARCHAR(50)  NOT NULL DEFAULT 'available',
   cosignerName    VARCHAR(100),
   brokerFee       DECIMAL(10,2),
   FOREIGN KEY (apartmentID) REFERENCES Apartment(apartmentID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (landlordID)  REFERENCES Landlord(landlordID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (brokerID)    REFERENCES Broker(brokerID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (renterID)    REFERENCES Renter(renterID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE ListingImage (
   listingImageID    INT AUTO_INCREMENT,
   imageURL          VARCHAR(255) NOT NULL,
   listingID         INT NOT NULL,
   PRIMARY KEY (listingImageID),
   FOREIGN KEY (listingID) REFERENCES Listing(listingID)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);


CREATE TABLE Inquiry (
   inquiryID   INT AUTO_INCREMENT,
   listingID   INT NOT NULL,
   senderName  VARCHAR(100) NOT NULL,
   senderEmail VARCHAR(100) NOT NULL,
   message     TEXT         NOT NULL,
   sentAt      DATE         NOT NULL DEFAULT (CURRENT_DATE),
   isRead      BOOLEAN      NOT NULL DEFAULT FALSE,
   PRIMARY KEY(inquiryID),
   FOREIGN KEY (listingID) REFERENCES Listing(listingID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE PerformanceReport (
   reportID            INT AUTO_INCREMENT,
   apartmentID         INT NOT NULL,
   brokerID            INT NOT NULL,
   applicationsCount   INT          NOT NULL DEFAULT 0,
   occupancyRate       DECIMAL(5,2),
   daysOnMarket        INT          NOT NULL DEFAULT 0,
   viewCount           INT          NOT NULL DEFAULT 0,
   PRIMARY KEY (reportID),
   FOREIGN KEY (apartmentID) REFERENCES Apartment(apartmentID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (brokerID)    REFERENCES Broker(brokerID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE Reports (
   reportID              INT AUTO_INCREMENT,
   adminID               INT NOT NULL,
   senderID              INT NOT NULL,
   listingID             INT,
   performanceReportID   INT,
   reportType            VARCHAR(50)  NOT NULL,
   reportReason          VARCHAR(255) NOT NULL,
   reportedUserID        INT,
   PRIMARY KEY (reportID),
   FOREIGN KEY (adminID) REFERENCES Admin(adminID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (senderID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (listingID) REFERENCES Listing(listingID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (performanceReportID) REFERENCES PerformanceReport(reportID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (reportedUserID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);


CREATE TABLE ModerationAction (
   actionID      INT AUTO_INCREMENT,
   adminID       INT NOT NULL,
   userID        INT NOT NULL,
   listingID     INT,
   reportID      INT,
   actionType    VARCHAR(50)  NOT NULL,
   actionStatus  VARCHAR(50)  NOT NULL DEFAULT 'Pending',
   actionDate    DATE         DEFAULT (CURRENT_DATE),
   actionReason  VARCHAR(255),
   PRIMARY KEY (actionID),
   FOREIGN KEY (adminID) REFERENCES Admin(adminID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (userID) REFERENCES Users(userID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (listingID) REFERENCES Listing(listingID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT,
   FOREIGN KEY (reportID) REFERENCES Reports(reportID)
       ON UPDATE CASCADE
       ON DELETE RESTRICT
);


CREATE TABLE ApartmentAmenities (
   apartmentID  INT NOT NULL,
   featureID    INT NOT NULL,
   PRIMARY KEY (apartmentID, featureID),
   FOREIGN KEY (apartmentID) REFERENCES Apartment(apartmentID)
       ON UPDATE CASCADE
       ON DELETE CASCADE,
   FOREIGN KEY (featureID)   REFERENCES ApartmentFeatures(featureID)
       ON UPDATE CASCADE
       ON DELETE CASCADE
);
-- END of Problem 1 Solution --
