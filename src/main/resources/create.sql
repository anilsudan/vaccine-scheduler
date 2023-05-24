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
    CaregiverID VARCHAR(255) REFERENCES Caregivers NOT NULL,
    Date DATE NOT NULL,
    AppointmentID VARCHAR(36) PRIMARY KEY,
    CONSTRAINT scheduled UNIQUE(CaregiverID, DATE)
);

CREATE TABLE Appointments (
    AppointmentID VARCHAR(36) REFERENCES Availabilities NOT NULL PRIMARY KEY,
    VaccineType VARCHAR(255) REFERENCES Vaccines,
    PatientID VARCHAR(255) REFERENCES Patients,
);