# Smart CPU Scheduling Simulator

A web-based CPU scheduling simulator built using Python, Flask, MySQL, HTML, CSS, and JavaScript.

## Features

- FCFS (First Come, First Served)
- SJF (Shortest Job First)
- SRTF (Shortest Remaining Time First)
- Priority Scheduling
- Round Robin Scheduling
- Process scheduling results and performance metrics
- Gantt chart visualization
- Save and load workloads
- Simulation history
- Export simulation history to CSV
- Export individual simulation results to CSV

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** MySQL
- **Database Connector:** MySQL Connector/Python

## Prerequisites

Install the following before running the project:

- Python 3.10 or a compatible version
- MySQL Server 8.0 or compatible version
- Git

## Installation and Setup

### 1. Clone the repository

```bash
git clone GITHUB_REPOSITORY_URL
cd smart-cpu-scheduling-simulator
```

Replace `GITHUB_REPOSITORY_URL` with the URL of GitHub repository.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Start MySQL Server.

Open MySQL Workbench and run the SQL script in `database/schema.sql` to create the database and tables.

### 5. Configure environment variables

Copy `.env.example` to a new file named `.env`.

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and enter your own MySQL username and password.

Example:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=cpu_scheduler_db
```



### 6. Run the application

From the project root, with your virtual environment activated:

```bash
python app.py
```

Open the local address displayed in the terminal, typically:

`http://127.0.0.1:5000/`

## Project Structure

```text
smart-cpu-scheduling-simulator/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── database/
│   ├── db.py
│   └── schema.sql
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── scheduler/
├── services/
└── tests/
```

## Notes

- Each developer must configure their own MySQL credentials.
- The database schema creates the tables but does not include existing simulation data.



