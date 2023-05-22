CREATE TABLE Vaccines (
    Name VARCHAR(255) PRIMARY KEY,
    Doses INT CHECK (Doses >=0)
);

CREATE TABLE Caregivers (
    Username VARCHAR(255) PRIMARY KEY,
    Salt BINARY(16),
    Hash BINARY(16)
);

CREATE TABLE Patients (
    Username VARCHAR(255) PRIMARY KEY,
    Salt BINARY(16),
    Hash BINARY(16)
);

CREATE TABLE Availabilities (
    CaregiverID VARCHAR(255) REFERENCES Caregivers,
    Date DATE,
    PRIMARY KEY (CaregiverID, Date)
);

CREATE TABLE Appointments (
    AppointmentID INT UNIQUE
    Date DATE
    CaregiverID VARCHAR(255)
    VaccineType VARCHAR(255) REFERENCES Vaccines,
    PatientID VARCHAR(255) REFERENCES Patients,
	FOREIGN KEY (CaregiverID, Date) REFERENCES Availabilities (CaregiverID, Date)
);