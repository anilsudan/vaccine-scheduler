# vaccine-scheduler

Created for UW CSE414 HW6 (Spring 2023)

Designed to run on Python 3.10.11 using SQL Server

## Setup (macOS)

1. Clone repository - `https://www.github.com/anilsudan/vaccine-scheduler.git`
2. Install Dependencies
    - pip: `python3 -m pip -r requirements.txt`
    - Conda: `conda install pymssql; conda install -c conda-forge python-decouple`
3. Create a `.env` file in the root directory containing the following information about your Azure SQL database
```commandline
Server=<name of your azure server, without .database.windows.net>
DBName=<Name of your Database>
UserID=<Database username>
Password=<Database password>
```
4. Run `src/main/resources/create.sql` on your Azure SQL database.

## Usage

Run `src/main/scheduler/Scheduler.py`

