
CREATE DATABASE IF NOT EXISTS cpu_scheduler_db;
USE cpu_scheduler_db;

CREATE TABLE IF NOT EXISTS workloads (
    workload_id INT NOT NULL AUTO_INCREMENT,
    workload_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workload_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS processes (
    process_id INT NOT NULL AUTO_INCREMENT,
    workload_id INT NOT NULL,
    pid VARCHAR(20) NOT NULL,
    arrival_time INT NOT NULL,
    burst_time INT NOT NULL,
    priority INT NOT NULL DEFAULT '0',
    PRIMARY KEY (process_id),
    UNIQUE KEY uq_workload_pid (workload_id, pid),
    CONSTRAINT fk_process_workload
        FOREIGN KEY (workload_id)
        REFERENCES workloads (workload_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_arrival_time CHECK (arrival_time >= 0),
    CONSTRAINT chk_burst_time CHECK (burst_time > 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id INT NOT NULL AUTO_INCREMENT,
    workload_id INT NOT NULL,
    algorithm VARCHAR(30) NOT NULL,
    time_quantum INT DEFAULT NULL,
    average_waiting_time DECIMAL(12,4) NOT NULL,
    average_turnaround_time DECIMAL(12,4) NOT NULL,
    average_response_time DECIMAL(12,4) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id),
    KEY fk_run_workload (workload_id),
    CONSTRAINT fk_run_workload
        FOREIGN KEY (workload_id)
        REFERENCES workloads (workload_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_time_quantum
        CHECK (time_quantum IS NULL OR time_quantum > 0)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS simulation_results (
    result_id INT NOT NULL AUTO_INCREMENT,
    run_id INT NOT NULL,
    pid VARCHAR(20) NOT NULL,
    arrival_time INT NOT NULL,
    burst_time INT NOT NULL,
    priority INT NOT NULL DEFAULT '0',
    start_time INT NOT NULL,
    completion_time INT NOT NULL,
    turnaround_time INT NOT NULL,
    waiting_time INT NOT NULL,
    response_time INT NOT NULL,
    PRIMARY KEY (result_id),
    KEY fk_result_run (run_id),
    CONSTRAINT fk_result_run
        FOREIGN KEY (run_id)
        REFERENCES simulation_runs (run_id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;
