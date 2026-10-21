
document.addEventListener("DOMContentLoaded", () => {
    const $ = (id) => document.getElementById(id);

    const processTable = $("process-table");
    const addButton = $("add-process");
    const resetButton = $("reset-processes");
    const runButton = $("run-simulation");
    const algorithmSelect = $("algorithm");
    const workloadName = $("workload-name");
    const savedWorkloadSelect = $("saved-workload");
    const loadWorkloadButton = $("load-workload");
    const refreshHistoryButton = $("refresh-history");
    const exportHistoryButton = $("export-history");
    const exportProcessDetailsButton = $("export-process-details");
    const exportRunSelect = $("export-run-id");
    const quantumField = $("quantum-field");
    const quantumInput = $("quantum");
    const message = $("message");

    function showMessage(text, isError = false) {
        message.textContent = text;
        message.classList.toggle("error", isError);
    }

    function addProcess(pid = `P${processTable.children.length + 1}`) {
        const row = document.createElement("tr");

        const values = [
            { className: "pid", value: pid, type: "text" },
            { className: "arrival", value: 0, type: "number", min: 0 },
            { className: "burst", value: 1, type: "number", min: 1 },
            { className: "priority", value: 1, type: "number" }
        ];

        for (const item of values) {
            const cell = document.createElement("td");
            const input = document.createElement("input");

            input.type = item.type;
            input.className = item.className;
            input.value = item.value;
            input.required = true;

            if (item.min !== undefined) input.min = item.min;
            if (item.type === "number") input.step = "1";

            cell.appendChild(input);
            row.appendChild(cell);
        }

        const actionCell = document.createElement("td");
        const removeButton = document.createElement("button");

        removeButton.type = "button";
        removeButton.textContent = "Remove";
        removeButton.className = "button secondary";

        removeButton.addEventListener("click", () => row.remove());

        actionCell.appendChild(removeButton);
        row.appendChild(actionCell);
        processTable.appendChild(row);
    }

    function collectProcesses() {
        const rows = [...processTable.querySelectorAll("tr")];

        if (rows.length === 0) {
            throw new Error("Add at least one process.");
        }

        const seen = new Set();

        return rows.map((row) => {
            const pid = row.querySelector(".pid").value.trim();
            const arrival = Number(row.querySelector(".arrival").value);
            const burst = Number(row.querySelector(".burst").value);
            const priority = Number(row.querySelector(".priority").value);

            if (!pid) throw new Error("Process ID cannot be empty.");
            if (seen.has(pid)) throw new Error(`Duplicate process ID: ${pid}`);
            seen.add(pid);

            if (!Number.isInteger(arrival) || arrival < 0) {
                throw new Error(`Arrival time for ${pid} must be a non-negative integer.`);
            }

            if (!Number.isInteger(burst) || burst <= 0) {
                throw new Error(`Burst time for ${pid} must be a positive integer.`);
            }

            if (!Number.isInteger(priority)) {
                throw new Error(`Priority for ${pid} must be an integer.`);
            }

            return {
                pid,
                arrival_time: arrival,
                burst_time: burst,
                priority
            };
        });
    }

    function renderResults(result) {
        $("results-placeholder").hidden = true;
        $("results-content").hidden = false;

        const gantt = $("gantt-chart");
        gantt.replaceChildren();

        for (const segment of result.gantt) {
            const block = document.createElement("div");
            block.className = "gantt-block";
            block.style.flexGrow = Math.max(1, segment.end - segment.start);
            block.title = `${segment.pid}: ${segment.start}–${segment.end}`;

            const label = document.createElement("strong");
            label.textContent = segment.pid;

            const times = document.createElement("span");
            times.textContent = `${segment.start} – ${segment.end}`;

            block.append(label, times);
            gantt.appendChild(block);
        }

        const metrics = $("metrics");
        metrics.replaceChildren();

        const metricLabels = [
            ["Average Waiting Time", result.averages.waiting_time],
            ["Average Turnaround Time", result.averages.turnaround_time],
            ["Average Response Time", result.averages.response_time]
        ];

        for (const [label, value] of metricLabels) {
            const card = document.createElement("div");
            card.className = "metric-card";

            const heading = document.createElement("h4");
            heading.textContent = label;

            const number = document.createElement("p");
            number.textContent = Number(value).toFixed(2);

            card.append(heading, number);
            metrics.appendChild(card);
        }

        const resultsTable = $("results-table");
        resultsTable.replaceChildren();

        for (const process of result.processes) {
            const row = document.createElement("tr");

            const columns = [
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.start_time,
                process.completion_time,
                process.turnaround_time,
                process.waiting_time,
                process.response_time
            ];

            for (const value of columns) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            }

            resultsTable.appendChild(row);
        }
    }
    
    async function loadSavedWorkloads() {
        savedWorkloadSelect.innerHTML =
            '<option value="">Select a saved workload</option>';

        try {
            const response = await fetch("/api/workloads");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Could not load workloads.");
            }

            for (const workload of data.workloads) {
                const option = document.createElement("option");
                option.value = workload.workload_id;
                option.textContent =
                    `${workload.workload_name} (ID: ${workload.workload_id})`;

                savedWorkloadSelect.appendChild(option);
            }

            if (data.workloads.length === 0) {
                savedWorkloadSelect.innerHTML =
                    '<option value="">No saved workloads found</option>';
            }
        } catch (error) {
            savedWorkloadSelect.innerHTML =
                '<option value="">Failed to load workloads</option>';
            showMessage(error.message, true);
        }
    }

    async function loadSelectedWorkload() {
        const workloadId = savedWorkloadSelect.value;

        if (!workloadId) {
            showMessage("Select a saved workload first.", true);
            return;
        }

        loadWorkloadButton.disabled = true;
        loadWorkloadButton.textContent = "Loading...";

        try {
            const response = await fetch(`/api/workloads/${workloadId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Could not load workload.");
            }

            processTable.replaceChildren();

            for (const process of data.processes) {
                addProcess(process.pid);
                const row = processTable.lastElementChild;

                row.querySelector(".arrival").value = process.arrival_time;
                row.querySelector(".burst").value = process.burst_time;
                row.querySelector(".priority").value = process.priority;
            }

            workloadName.value = data.workload.workload_name;

            showMessage(
                `Loaded "${data.workload.workload_name}" with ${data.processes.length} processes.`
            );
        } catch (error) {
            showMessage(error.message, true);
        } finally {
            loadWorkloadButton.disabled = false;
            loadWorkloadButton.textContent = "Load Workload";
        }
    }
    
    async function loadExportRunOptions() {
        exportRunSelect.innerHTML =
            '<option value="">Select a simulation run</option>';

        try {
            const response = await fetch("/api/history");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Could not load simulation runs."
                );
            }

            for (const run of data.history || []) {
                const option = document.createElement("option");
                option.value = run.run_id;
                option.textContent =
                    `Run ${run.run_id} — ${run.workload_name} (${run.algorithm})`;

                exportRunSelect.appendChild(option);
            }
        } catch (error) {
            showMessage(error.message, true);
        }
    }

    function downloadCsv(url) {
        window.location.href = url;
    }
    
    exportHistoryButton.addEventListener("click", () => {
        downloadCsv("/api/export/history");
    });

    exportProcessDetailsButton.addEventListener("click", () => {
        const runId = exportRunSelect.value;

        if (!runId) {
            showMessage("Select a simulation run first.", true);
            return;
        }

        downloadCsv(`/api/export/simulation/${runId}`);
    });




   
    async function loadHistory() {
        const historyMessage = $("history-message");
        historyMessage.textContent = "Loading history...";

        try {
            const response = await fetch("/api/history");
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Could not load history.");
            }

            const table = $("history-table");
            table.replaceChildren();

            if (!data.history || data.history.length === 0) {
                historyMessage.textContent = "No simulation history yet.";
                return;
            }

            historyMessage.textContent = `${data.count} saved simulation(s).`;

            for (const run of data.history) {
                const row = document.createElement("tr");

                const values = [
                    run.run_id,
                    run.workload_name,
                    run.algorithm,
                    Number(run.average_waiting_time).toFixed(2),
                    Number(run.average_turnaround_time).toFixed(2),
                    Number(run.average_response_time).toFixed(2),
                    run.created_at
                ];

                for (const value of values) {
                    const cell = document.createElement("td");
                    cell.textContent = value ?? "—";
                    row.appendChild(cell);
                }

                // Create the Delete button.
                const actionCell = document.createElement("td");
                const deleteButton = document.createElement("button");

                deleteButton.type = "button";
                deleteButton.textContent = "Delete";
                deleteButton.className = "button secondary";

                deleteButton.addEventListener("click", async () => {
                    const confirmed = confirm(
                        `Delete simulation run ${run.run_id}? This cannot be undone.`
                    );

                    if (!confirmed) {
                        return;
                    }

                    deleteButton.disabled = true;
                    deleteButton.textContent = "Deleting...";

                    try {
                        const deleteResponse = await fetch(
                            `/api/history/${run.run_id}`,
                            { method: "DELETE" }
                        );

                        const result = await deleteResponse.json();

                        if (!deleteResponse.ok) {
                            throw new Error(
                                result.error || "Could not delete simulation."
                            );
                        }

                        historyMessage.textContent =
                            result.message || "Simulation deleted successfully.";

                        await loadHistory();
                    } catch (error) {
                        alert(`Delete failed: ${error.message}`);
                        deleteButton.disabled = false;
                        deleteButton.textContent = "Delete";
                    }
                });

                actionCell.appendChild(deleteButton);
                row.appendChild(actionCell);
                table.appendChild(row);
            }
        } catch (error) {
            historyMessage.textContent = `History error: ${error.message}`;
        }
    }


    async function checkApi() {
        const status = $("api-status");

        try {
            const response = await fetch("/api/health");
            if (!response.ok) throw new Error("API unavailable");

            status.textContent = "API Connected";
            status.classList.add("connected");
        } catch {
            status.textContent = "API Disconnected";
        }
    }

    addButton.addEventListener("click", () => {
        addProcess();
        showMessage("Process added.");
    });

    resetButton.addEventListener("click", () => {
        processTable.replaceChildren();
        addProcess("P1");
        $("results-content").hidden = true;
        $("results-placeholder").hidden = false;
        showMessage("Processes reset.");
    });

    algorithmSelect.addEventListener("change", () => {
        quantumField.hidden = algorithmSelect.value !== "Round Robin";
    });

    runButton.addEventListener("click", async () => {
        try {
            const processes = collectProcesses();
            const algorithm = algorithmSelect.value;
            const body = {
                workload_name: workloadName.value.trim(),
                algorithm,
                processes
            };

            if (!body.workload_name) {
                throw new Error("Enter a workload name.");
            }

            if (algorithm === "Round Robin") {
                body.quantum = Number(quantumInput.value);

                if (!Number.isInteger(body.quantum) || body.quantum <= 0) {
                    throw new Error("Time quantum must be a positive integer.");
                }
            }

            runButton.disabled = true;
            runButton.textContent = "Running...";
            showMessage("Running simulation...");

            const response = await fetch("/api/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Simulation failed.");
            }

            renderResults(result);
            showMessage(
                `Simulation saved successfully. Run ID: ${result.run_id}`
            );

            await loadHistory();
        } catch (error) {
            showMessage(error.message, true);
        } finally {
            runButton.disabled = false;
            runButton.textContent = "Run Simulation";
        }
    });

   
    refreshHistoryButton.addEventListener("click", async () => {
        await loadHistory();
        await loadExportRunOptions();
    });


    addProcess("P1");

    loadWorkloadButton.addEventListener("click", loadSelectedWorkload);

    checkApi();
    loadHistory();
    loadExportRunOptions();
    loadSavedWorkloads();
});
