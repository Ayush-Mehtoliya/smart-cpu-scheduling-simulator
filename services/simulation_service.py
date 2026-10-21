
from database.db import get_connection


def save_simulation(workload_name, algorithm, processes, result):
    """Save a workload, its processes, and simulation results to MySQL."""

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO workloads (workload_name) VALUES (%s)",
            (workload_name,),
        )
        workload_id = cursor.lastrowid

        for process in processes:
            cursor.execute(
                """
                INSERT INTO processes
                    (workload_id, pid, arrival_time, burst_time, priority)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    workload_id,
                    str(process["pid"]),
                    process["arrival_time"],
                    process["burst_time"],
                    process.get("priority", 0),
                ),
            )

        averages = result["averages"]

        cursor.execute(
            """
            INSERT INTO simulation_runs (
                workload_id, algorithm, time_quantum,
                average_waiting_time, average_turnaround_time,
                average_response_time
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                workload_id,
                algorithm,
                result.get("quantum"),
                averages["waiting_time"],
                averages["turnaround_time"],
                averages["response_time"],
            ),
        )
        run_id = cursor.lastrowid

        original_processes = {
            str(p["pid"]): p for p in processes
        }

        for process in result["processes"]:
            original = original_processes[str(process["pid"])]

            cursor.execute(
                """
                INSERT INTO simulation_results (
                    run_id, pid, arrival_time, burst_time, priority,
                    start_time, completion_time, turnaround_time,
                    waiting_time, response_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    str(process["pid"]),
                    process["arrival_time"],
                    process["burst_time"],
                    original.get("priority", 0),
                    process["start_time"],
                    process["completion_time"],
                    process["turnaround_time"],
                    process["waiting_time"],
                    process["response_time"],
                ),
            )

        connection.commit()

        return {
            "workload_id": workload_id,
            "run_id": run_id,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
