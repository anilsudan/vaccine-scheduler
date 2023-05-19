# vaccine-scheduler

Command-line application for scheduling COVID-19 vaccination appointments.  Written for CSE414 at UW in Spring 2023.
Built from https://github.com/aaditya1004/vaccine-scheduler-python

Written using Python 3.10 (pymssql has bugs with 3.11 on arm64, might work for you though)

## Setup (macOS)

1. Clone repository - `https://www.github.com/anilsudan/vaccine-scheduler.git`
2. Install Dependencies
    - pip: `python3 -m pip -r requirements.txt`
    - Conda: `conda install pymssql; conda install -c conda-forge python-decouple`
3. Create a `.env` file in the root directory containing the following information about your Azure SQL database
   ```commandline
   Server=<Server name, without '.database.windows.net'>
   DBName=<Database name>
   UserID=<Database username>
   Password=<Database password>
   ```
4. Run `src/main/resources/create.sql` on your Azure SQL database.

## Usage

Run `src/main/scheduler/Scheduler.py`


## Todo

Add support for self-hosted SQL Server backends.
