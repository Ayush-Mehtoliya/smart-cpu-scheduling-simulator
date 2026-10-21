
def priority_scheduling(processes):
    """Non-preemptive priority scheduling; smaller number = higher priority."""
    if not isinstance(processes, list) or not processes:
        raise ValueError("Processes must be a non-empty list.")

    required = {"pid", "arrival_time", "burst_time", "priority"}
    validated = []
    seen = set()

    for index, process in enumerate(processes):
        if not isinstance(process, dict) or not required.issubset(process):
            raise ValueError(
                f"Process at index {index} must contain "
                "pid, arrival_time, burst_time, priority."
            )

        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]
        priority = process["priority"]

        if not isinstance(pid, (str, int)) or isinstance(pid, bool):
            raise ValueError("Process ID must be a string or integer.")
        if isinstance(pid, str) and not pid.strip():
            raise ValueError("Process ID cannot be empty.")
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        if type(arrival) is not int or arrival < 0:
            raise ValueError("Arrival time must be a non-negative integer.")
        if type(burst) is not int or burst <= 0:
            raise ValueError("Burst time must be a positive integer.")
        if type(priority) is not int:
            raise ValueError("Priority must be an integer.")

        seen.add(pid)
        validated.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "priority": priority,
            "_order": index,
        })

    remaining = validated.copy()
    current_time = 0
    results = []
    gantt = []

    while remaining:
        ready = [
            p for p in remaining
            if p["arrival_time"] <= current_time
        ]

        if not ready:
            next_arrival = min(p["arrival_time"] for p in remaining)
            gantt.append({
                "pid": "IDLE",
                "start": current_time,
                "end": next_arrival,
            })
            current_time = next_arrival
            continue

        process = min(
            ready,
            key=lambda p: (
                p["priority"],
                p["arrival_time"],
                p["_order"],
            ),
        )
        remaining.remove(process)

        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

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
            "priority": process["priority"],
            "start_time": start,
            "completion_time": completion,
            "turnaround_time": turnaround,
            "waiting_time": waiting,
            "response_time": response,
        })

        current_time = completion

    count = len(results)

    return {
        "algorithm": "Priority",
        "processes": results,
        "gantt": gantt,
        "averages": {
            "waiting_time": sum(p["waiting_time"] for p in results) / count,
            "turnaround_time": sum(p["turnaround_time"] for p in results) / count,
            "response_time": sum(p["response_time"] for p in results) / count,
        },
    }
