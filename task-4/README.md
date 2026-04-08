# Distributed Task Queue

## Objective
The goal is to implement a robust producer-consumer task queue that distributes units of work across multiple independent background worker processes. The system supports task serialization, failure handling with exponential backoff, Dead-Letter Queue (DLQ) routing, and persistent result backends.

## Implemented Solution
The solution is a fully functional distributed system that utilizes:

1. **Multiprocessing**: Spawns multiple worker processes to handle tasks concurrently, mirroring a real-world distributed environment.
2. **Task Serialization**: Uses `pickle` to serialize task metadata (function names, arguments, IDs, and retry counts) for reliable IPC (Inter-Process Communication).
3. **Broker Simulation**: A `multiprocessing.Manager().Queue()` acts as the message broker, facilitating the producer-consumer pattern between the main process and workers.
4. **Exponential Backoff & Retries**: Implements a retry loop within workers. When a task fails (e.g., a simulated `ConnectionError`), the system waits for an increasing amount of time (`2^retries`) before re-enqueuing the task.
5. **Dead-Letter Queue (DLQ)**: After exceeding the maximum retry limit (3), the task is marked as `DEAD_LETTER` and permanently stopped, preventing infinite loops on fatal errors.
6. **Result Backend**: Uses an `SQLite` database (`results.db`) to persist task statuses, durations, and results, allowing the dashboard to reconstruct the state even across runs.
7. **Dashboard**: A structured CLI view that queries the SQLite backend to display Task IDs, Function Names, Statuses, Retry Counts, and Durations.

## Requirements
- Python 3.8+
- Windows/Linux/macOS (Multiprocessing compatible)

## Setup Instructions
1. Navigate to the `task-4` folder:
   ```bash
   cd task-4
   ```
2. Run the system:
   ```bash
   python queue_system.py
   ```

## Dependencies
- `sqlite3` (Built-in)
- `multiprocessing` (Built-in)
- `pickle` (Built-in)
- `time`, `os`, `uuid`, `random` (Built-in)

## Runtime Output
```text
=== Broker ===
[BROKER] Listening on redis://localhost:6379/0
[BROKER] Queue "default" — 0 pending, 3 workers connected
=== Producer ===
>>> queue.enqueue(generate_thumbnail, image_id=4521, size=(256, 256))
Task queued: <Task id=a8f3c1 func=generate_thumbnail status=PENDING>
>>> queue.enqueue(send_email, to=bob@co.com, template=welcome)
Task queued: <Task id=b7d4e2 func=send_email status=PENDING>
>>> queue.enqueue(generate_report, )
Task queued: <Task id=c9e5f3 func=generate_report status=PENDING>
[WORKER-1] Starting...
[WORKER-2] Starting...
[WORKER-1] Picked up task a8f3c1 (generate_thumbnail)
[WORKER-1] Task a8f3c1 completed in 1.34s — result: /thumbs/4521_256x256.jpg    
[WORKER-2] Picked up task b7d4e2 (send_email)
[WORKER-2] Task b7d4e2 FAILED (ConnectionError) — retry 1/3 in 2s
[WORKER-1] Picked up task c9e5f3 (generate_report)
[WORKER-1] Task c9e5f3 FAILED (ValueError) — retry 1/3 in 2s
[WORKER-3] Starting...
[WORKER-2] Picked up task b7d4e2 (send_email)
[WORKER-2] Task b7d4e2 FAILED (ConnectionError) — retry 2/3 in 4s
[WORKER-2] Picked up task b7d4e2 (send_email)
[WORKER-2] Task b7d4e2 completed in 6.82s — result: email_sent
[WORKER-2] Picked up task c9e5f3 (generate_report)
[WORKER-2] Task c9e5f3 FAILED (ValueError) — retry 2/3 in 4s
[WORKER-3] Picked up task c9e5f3 (generate_report)
[WORKER-3] Task c9e5f3 FAILED (ValueError) — retry 3/3 in 8s
[WORKER-1] Picked up task c9e5f3 (generate_report)
[WORKER-1] Task c9e5f3 permanently FAILED — moving to Dead Letter Queue
=== Dashboard ===
+----------+--------+-----------+--------+-------------+
| Task ID  | Func   | Status    | Retries| Duration    |
+----------+--------+-----------+--------+-------------+
| a8f3c1   | genera | SUCCESS   | 0      | 1.34s       |
| b7d4e2   | send_e | SUCCESS   | 2      | 6.82s       |
| c9e5f3   | genera | DEAD_LETTER | 3      | —           |
+----------+--------+-----------+--------+-------------+
```
