# vaccine-scheduler

Created for UW CSE414 HW6 (Spring 2023)

Designed to run on Python 3.10.11 using SQL Server

## Setup (macOS, venv)

1. Clone repository - `git clone https://www.github.com/anilsudan/vaccine-scheduler.git`

2. Create venv within repository folder - `python3.10 -m venv {env_name}`

3. Add environment variables to `{env_name}\bin\activate` to configure Azure details.

- Add the following lines to the end of activate
```commandline
export Server<server_name>
export DBName=<db_name>
export UserID=<db_username>
export Password=<db_pass> 
```

- Add the following lines within the `deactivate()` function in the activate script.
```commandline
    unset Server
    unset DBName
    unset Username
    unset Password
```

4. Activate venv and run dependencies:

```commandline
source {env_name}\bin\activate
pip3 install -r requirements.txt
```

## Usage

