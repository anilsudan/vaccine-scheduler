# vaccine-scheduler

Command-line application for scheduling COVID-19 vaccination appointments.  Written for CSE414 at UW in Spring 2023.
Built from https://github.com/aaditya1004/vaccine-scheduler-python

Written using Python 3.10 (pymssql has bugs with 3.11 on arm64, might work for you though)

## Setup (macOS)

1. Clone repository - `git clone https://www.github.com/anilsudan/vaccine-scheduler.git`


2. Create environment - 
   
   venv - `cd vaccine-scheduler && python3 -m venv env`
   
   conda - `conda create vaccine-scheduler`


3. Install dependencies

   venv - `source env/bin/activate && pip3 -r requirements.txt`

   conda - `conda activate vaccine-scheduler && conda install pymssql &&  conda install -c conda-forge python-decouple`


4. Configure Database settings
   
   Create a file named `.env` in the root of the application directory, with the following information:
   ```commandline
   Server=<AZURE_SERVER_NAME>
   DBName=<SQL_DB_NAME>
   UserID=<DB_USERNAME>
   Pass=<DB_PASS>
   ```
   The server name is the part of the domain name before ".database.windows.net"


5. Run `src/main/resources/create.sql` on your Azure SQL database.


## Usage

venv - `./run.sh`

conda - `conda activate vaccine-scheduler && python3 src/main/scheduler/Scheduler.py`


## Todo

Add support for self-hosted SQL Server backends.
