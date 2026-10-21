
from collections import deque


def round_robin(processes, quantum):
    """Simulate Round Robin CPU scheduling."""

    if not isinstance(processes, list) or not processes:
        raise ValueError("Processes must be a non-empty list.")

    if type(quantum) is not int or quantum <= 0:
        raise ValueError("Time quantum must be a positive integer.")

    required = {"pid", "arrival_time", "burst_time"}
    validated = []
    seen = set()

    for index, process in enumerate(processes):
        if not isinstance(process, dict) or not required.issubset(process):
            raise ValueError(
                f"Process at index {index} must contain "
                "pid, arrival_time, and burst_time."
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

    # Sort by arrival time, preserving input order for ties.
    pending = sorted(
        validated,
        key=lambda p: (p["arrival_time"], p["_order"]),
    )

    remaining_time = {p["pid"]: p["burst_time"] for p in validated}
    first_start = {}
    completion_time = {}
    ready_queue = deque()
    gantt = []

    current_time = 0
    next_process = 0

    while next_process < len(pending) or ready_queue:

        # If the ready queue is empty, advance to the next arrival.
        if not ready_queue:
            next_arrival = pending[next_process]["arrival_time"]

            if current_time < next_arrival:
                gantt.append({
                    "pid": "IDLE",
                    "start": current_time,
                    "end": next_arrival,
                })
                current_time = next_arrival

            while (
                next_process < len(pending)
                and pending[next_process]["arrival_time"] <= current_time
            ):
                ready_queue.append(pending[next_process]["pid"])
                next_process += 1

        pid = ready_queue.popleft()

        if pid not in first_start:
            first_start[pid] = current_time

        start = current_time
        run_time = min(quantum, remaining_time[pid])
        current_time += run_time
        remaining_time[pid] -= run_time

        gantt.append({
            "pid": pid,
            "start": start,
            "end": current_time,
        })

        # Enqueue newly arrived processes before re-queuing this process.
        while (
            next_process < len(pending)
            and pending[next_process]["arrival_time"] <= current_time
        ):
            ready_queue.append(pending[next_process]["pid"])
            next_process += 1

        if remaining_time[pid] > 0:
            ready_queue.append(pid)
        else:
            completion_time[pid] = current_time

    results = []

    # Return metrics in the original input order.
    for process in validated:
        pid = process["pid"]
        arrival = process["arrival_time"]
        burst = process["burst_time"]
        completion = completion_time[pid]
        turnaround = completion - arrival
        waiting = turnaround - burst
        response = first_start[pid] - arrival

        results.append({
            "pid": pid,
            "arrival_time": arrival,
            "burst_time": burst,
            "start_time": first_start[pid],
            "completion_time": completion,
            "turnaround_time": turnaround,
            "waiting_time": waiting,
            "response_time": response,
        })

    count = len(results)

    return {
        "algorithm": "Round Robin",
        "quantum": quantum,
        "processes": results,
        "gantt": gantt,
        "averages": {
            "waiting_time": sum(
                p["waiting_time"] for p in results
            ) / count,
            "turnaround_time": sum(
                p["turnaround_time"] for p in results
            ) / count,
            "response_time": sum(
                p["response_time"] for p in results
            ) / count,
        },
    }
