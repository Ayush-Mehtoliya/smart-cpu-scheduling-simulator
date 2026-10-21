from flask import Flask, jsonify, request
from database.db import get_connection
from services.simulation_service import save_simulation
import csv
import io

from flask import Flask, jsonify, request, Response
from scheduler import (
    fcfs,
    sjf,
    srtf,
    priority_scheduling,
    round_robin,
)

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)
@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "CPU Scheduling Simulator API is running"
    }), 200


@app.route("/api/db-health", methods=["GET"])
def database_health():
    connection = None

    try:
        connection = get_connection()

        if connection.is_connected():
            return jsonify({
                "status": "ok",
                "database": "cpu_scheduler_db",
                "message": "MySQL connection successful"
            }), 200

        return jsonify({
            "status": "error",
            "message": "MySQL connection is not active"
        }), 500

    except Exception:
        app.logger.exception("Database health check failed")
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500

    finally:
        if connection is not None:
            try:
                if connection.is_connected():
                    connection.close()
            except Exception:
                app.logger.exception("Failed to close database connection")


@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    algorithm = data.get("algorithm")
    processes = data.get("processes")
    quantum = data.get("quantum")
    workload_name = data.get("workload_name", "Untitled Workload")

    if not isinstance(workload_name, str) or not workload_name.strip():
        return jsonify({
            "error": "workload_name must be a non-empty string."
        }), 400

    if not isinstance(processes, list) or not processes:
        return jsonify({
            "error": "processes must be a non-empty list."
        }), 400

    try:
        if algorithm == "FCFS":
            result = fcfs(processes)

        elif algorithm == "SJF":
            result = sjf(processes)

        elif algorithm == "SRTF":
            result = srtf(processes)

        elif algorithm == "Priority":
            result = priority_scheduling(processes)

        elif algorithm == "Round Robin":
            if (
                isinstance(quantum, bool)
                or not isinstance(quantum, (int, float))
                or quantum <= 0
            ):
                return jsonify({
                    "error": "Round Robin requires a positive quantum."
                }), 400

            result = round_robin(processes, quantum)

        else:
            return jsonify({
                "error": (
                    "Unsupported algorithm. Use FCFS, SJF, SRTF, "
                    "Priority, or Round Robin."
                )
            }), 400

        saved = save_simulation(
            workload_name.strip(),
            algorithm,
            processes,
            result,
        )

        if not isinstance(saved, dict):
            raise ValueError("save_simulation must return a dictionary.")

        if "workload_id" not in saved or "run_id" not in saved:
            raise ValueError(
                "save_simulation must return workload_id and run_id."
            )

        result["workload_id"] = saved["workload_id"]
        result["run_id"] = saved["run_id"]

        return jsonify(result), 200

    except (ValueError, TypeError) as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        app.logger.exception("Simulation or database save failed")
        return jsonify({
            "error": (
                "Simulation could not be completed or "
                "saved to the database."
            )
        }), 500
    
@app.route("/api/history", methods=["GET"])
def simulation_history():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                sr.run_id,
                sr.workload_id,
                w.workload_name,
                sr.algorithm,
                sr.time_quantum,
                sr.average_waiting_time,
                sr.average_turnaround_time,
                sr.average_response_time,
                sr.created_at
            FROM simulation_runs AS sr
            INNER JOIN workloads AS w
                ON sr.workload_id = w.workload_id
            ORDER BY sr.created_at DESC, sr.run_id DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert MySQL values into JSON-serializable values.
        for row in rows:
            if row["created_at"] is not None:
                row["created_at"] = row["created_at"].isoformat(
                    sep=" ", timespec="seconds"
                )

            for field in (
                "average_waiting_time",
                "average_turnaround_time",
                "average_response_time",
            ):
                if row[field] is not None:
                    row[field] = float(row[field])

        return jsonify({
            "count": len(rows),
            "history": rows,
        }), 200

    except Exception:
        app.logger.exception("Failed to retrieve simulation history")
        return jsonify({
            "error": "Could not retrieve simulation history."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            try:
                if connection.is_connected():
                    connection.close()
            except Exception:
                app.logger.exception(
                    "Failed to close history database connection"
                )



@app.route("/api/export/history", methods=["GET"])
def export_history_csv():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sr.run_id,
                w.workload_name,
                sr.algorithm,
                sr.average_waiting_time,
                sr.average_turnaround_time,
                sr.average_response_time,
                sr.created_at
            FROM simulation_runs AS sr
            JOIN workloads AS w
                ON sr.workload_id = w.workload_id
            ORDER BY sr.created_at DESC
        """)

        rows = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Run ID",
            "Workload Name",
            "Algorithm",
            "Average Waiting Time",
            "Average Turnaround Time",
            "Average Response Time",
            "Created At"
        ])

        for row in rows:
            writer.writerow([
                row["run_id"],
                row["workload_name"],
                row["algorithm"],
                row["average_waiting_time"],
                row["average_turnaround_time"],
                row["average_response_time"],
                row["created_at"]
            ])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                    'attachment; filename="simulation_history.csv"'
            }
        )

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route("/api/export/simulation/<int:run_id>", methods=["GET"])
def export_simulation_csv(run_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sr.run_id,
                sr.algorithm,
                sr.time_quantum,
                res.pid,
                res.arrival_time,
                res.burst_time,
                res.priority,
                res.start_time,
                res.completion_time,
                res.turnaround_time,
                res.waiting_time,
                res.response_time
            FROM simulation_runs AS sr
            JOIN simulation_results AS res
                ON sr.run_id = res.run_id
            WHERE sr.run_id = %s
            ORDER BY res.result_id
        """, (run_id,))

        rows = cursor.fetchall()

        if not rows:
            return jsonify({
                "error": "Simulation run not found or has no process results."
            }), 404

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Run ID",
            "Algorithm",
            "Time Quantum",
            "Process ID",
            "Arrival Time",
            "Burst Time",
            "Priority",
            "Start Time",
            "Completion Time",
            "Turnaround Time",
            "Waiting Time",
            "Response Time"
        ])

        for row in rows:
            writer.writerow([
                row["run_id"],
                row["algorithm"],
                row["time_quantum"],
                row["pid"],
                row["arrival_time"],
                row["burst_time"],
                row["priority"],
                row["start_time"],
                row["completion_time"],
                row["turnaround_time"],
                row["waiting_time"],
                row["response_time"]
            ])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                    f'attachment; filename="simulation_{run_id}_details.csv"'
            }
        )

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@app.route("/api/workloads", methods=["GET"])
def get_workloads():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT workload_id, workload_name, created_at
            FROM workloads
            ORDER BY workload_id DESC
        """)

        workloads = cursor.fetchall()

        for workload in workloads:
            if workload.get("created_at"):
                workload["created_at"] = (
                    workload["created_at"].isoformat(sep=" ")
                )

        return jsonify({
            "count": len(workloads),
            "workloads": workloads
        }), 200

    except Exception:
        app.logger.exception("Failed to fetch saved workloads")
        return jsonify({
            "error": "Could not load saved workloads."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


@app.route("/api/history/<int:run_id>", methods=["DELETE"])
def delete_simulation_history(run_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM simulation_runs WHERE run_id = %s",
            (run_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({
                "error": "Simulation history entry not found."
            }), 404

        connection.commit()

        return jsonify({
            "message": f"Simulation run {run_id} deleted successfully."
        }), 200

    except Exception as error:
        if connection:
            connection.rollback()

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()



@app.route("/api/workloads/<int:workload_id>", methods=["GET"])
def get_workload_details(workload_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT workload_id, workload_name, created_at
            FROM workloads
            WHERE workload_id = %s
        """, (workload_id,))

        workload = cursor.fetchone()

        if workload is None:
            return jsonify({
                "error": "Workload not found."
            }), 404

        cursor.execute("""
            SELECT pid, arrival_time, burst_time, priority
            FROM processes
            WHERE workload_id = %s
            ORDER BY process_id ASC
        """, (workload_id,))

        processes = cursor.fetchall()

        if workload.get("created_at"):
            workload["created_at"] = (
                workload["created_at"].isoformat(sep=" ")
            )

        return jsonify({
            "workload": workload,
            "processes": processes
        }), 200

    except Exception:
        app.logger.exception("Failed to load workload details")
        return jsonify({
            "error": "Could not load workload details."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()




if __name__ == "__main__":
    app.run(debug=True)
