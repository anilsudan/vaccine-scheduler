# Vaccine-Scheduler Database Design

## Vaccine
Contains vaccine information.  The doses var represents how many doses _are left to give out, not how many might be in stockpile._
- Name (VARCHAR) PRIMARY KEY
- Doses (INT) -- cannot be negative.

## Caregiver
Contains caregiver information used for login and registration
- Username (VARCHAR) PRIMARY KEY
- Salt BINARY(16)
- Hash BINARY(16)

## Patients
Contains patient information used for login and registration
- Username (VARCHAR) PRIMARY KEY
- Salt BINARY(16)
- Hash BINARY(16)

## Availabilities
When a caregiver marks themselves as available on a certain date, their Username and date are entered here.
- CaregiverID (VARCHAR) REFERENCES Caregiver
- Date (DATE)
- PRIMARY KEY (CaregiverID, Date, AppointmentID)

## Appointments
When an appointment is scheduled, add a row with the appointment ID, caregiver info, patient info and
vaccine type.
Appointment ID will come from hash(date, caregiverid) in python
- AppointmentID (INT) UNIQUE
- VaccineType (VARCHAR) REFERENCES Vaccine
- PatientID (VARCHAR) REFERENCES Patients
- CaregiverID (VARCHAR)
- Date (DATE)
- PRIMARY KEY(CaregiverID, Date)

## Usage
- To find all open appointments on a certain day, join Availabilities and Appointments on
CaregiverID and Date, then find those without a match.

## Find Open Appointments
```SQL
SELECT <whatever>
FROM Availabilities AV
LEFT OUTER JOIN Appointments AP ON AV.CaregiverID = AP.CaregiverID AND AV.Date = AP.Date
WHERE (VALUE is NULL); 
```