
def fcfs(processes):
    """
    Run First Come, First Served (FCFS) scheduling.

    Each process must contain:
        pid: process ID
        arrival_time: non-negative integer
        burst_time: positive integer

    Returns:
        A dictionary containing process metrics, Gantt-chart
        segments, and average waiting, turnaround, and response times.

    Assumption:
        Processes arriving at the same time retain input order.
    """
    if not isinstance(processes, list) or not processes:
        raise ValueError("Processes must be a non-empty list.")

    required_fields = {"pid", "arrival_time", "burst_time"}
    seen_pids = set()
    validated = []

    for index, process in enumerate(processes):
        if not isinstance(process, dict):
            raise ValueError(f"Process at index {index} must be a dictionary.")

        missing = required_fields - process.keys()
        if missing:
            raise ValueError(
                f"Process at index {index} is missing: {', '.join(sorted(missing))}"
            )

        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

        if not isinstance(pid, (str, int)) or isinstance(pid, bool):
            raise ValueError("Process ID must be a string or integer.")

        if isinstance(pid, str) and not pid.strip():
            raise ValueError("Process ID cannot be empty.")

        if pid in seen_pids:
            raise ValueError(f"Duplicate process ID: {pid}")

        if type(arrival) is not int or arrival < 0:
            raise ValueError("Arrival time must be a non-negative integer.")

        if type(burst) is not int or burst <= 0:
            raise ValueError("Burst time must be a positive integer.")

        seen_pids.add(pid)
        validated.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "_input_order": index,
        })

    # Sort by arrival time; preserve input order for ties.
    validated.sort(key=lambda p: (p["arrival_time"], p["_input_order"]))

    current_time = 0
    results = []
    gantt = []

    for process in validated:
        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

        # CPU remains idle if the next process has not arrived.
        if current_time < arrival:
            gantt.append({
                "pid": "IDLE",
                "start": current_time,
                "end": arrival,
            })
            current_time = arrival

        start = current_time
        completion = start + burst
        turnaround = completion - arrival
        waiting = turnaround - burst
        response = start - arrival

        gantt.append({
            "pid": pid,
            "start": start,
            "end": completion,
        })

        results.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "start_time": start,
            "completion_time": completion,
            "turnaround_time": turnaround,
            "waiting_time": waiting,
            "response_time": response,
        })

        current_time = completion

    count = len(results)

    return {
        "algorithm": "FCFS",
        "processes": results,
        "gantt": gantt,
        "averages": {
            "waiting_time": sum(p["waiting_time"] for p in results) / count,
            "turnaround_time": sum(p["turnaround_time"] for p in results) / count,
            "response_time": sum(p["response_time"] for p in results) / count,
        },
    }
