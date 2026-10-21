
def srtf(processes):
    """Preemptive Shortest Remaining Time First scheduling."""
    if not isinstance(processes, list) or not processes:
        raise ValueError("Processes must be a non-empty list.")

    required = {"pid", "arrival_time", "burst_time"}
    validated = []
    seen = set()

    for index, process in enumerate(processes):
        if not isinstance(process, dict) or not required.issubset(process):
            raise ValueError(
                f"Process at index {index} must contain pid, arrival_time, burst_time."
            )

        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]

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

        seen.add(pid)
        validated.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "_order": index,
        })

    remaining = {p["pid"]: p["burst_time"] for p in validated}
    first_start = {}
    completion = {}
    gantt = []
    current_time = 0
    finished = 0
    total = len(validated)

    while finished < total:
        ready = [
            p for p in validated
            if p["arrival_time"] <= current_time
            and remaining[p["pid"]] > 0
        ]

        if not ready:
            next_arrival = min(
                p["arrival_time"]
                for p in validated
                if remaining[p["pid"]] > 0
            )
            if current_time < next_arrival:
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
                remaining[p["pid"]],
                p["arrival_time"],
                p["_order"],
            ),
        )

        pid = process["pid"]
        first_start.setdefault(pid, current_time)

        # Execute for one time unit, then reconsider arrivals.
        if gantt and gantt[-1]["pid"] == pid and gantt[-1]["end"] == current_time:
            gantt[-1]["end"] += 1
        else:
            gantt.append({
                "pid": pid,
                "start": current_time,
                "end": current_time + 1,
            })

        remaining[pid] -= 1
        current_time += 1

        if remaining[pid] == 0:
            completion[pid] = current_time
            finished += 1

    results = []

    for process in validated:
        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]
        turnaround = completion[pid] - arrival

        results.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "start_time": first_start[pid],
            "completion_time": completion[pid],
            "turnaround_time": turnaround,
            "waiting_time": turnaround - burst,
            "response_time": first_start[pid] - arrival,
        })

    count = len(results)

    return {
        "algorithm": "SRTF",
        "processes": results,
        "gantt": gantt,
        "averages": {
            "waiting_time": sum(p["waiting_time"] for p in results) / count,
            "turnaround_time": sum(p["turnaround_time"] for p in results) / count,
            "response_time": sum(p["response_time"] for p in results) / count,
        },
    }
