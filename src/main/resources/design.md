# Vaccine-Scheduler Database Design

## Vaccine
- Name (VARCHAR) PRIMARY KEY
- Doses (INT)

## Caregiver
- Username (VARCHAR) PRIMARY KEY
- Salt BINARY(16)
- Hash BINARY(16)

## Patients
- Username (VARCHAR) PRIMARY KEY
- Salt BINARY(16)
- Hash BINARY(16)

## Availabilities
