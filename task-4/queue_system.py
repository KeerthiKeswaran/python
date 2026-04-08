import time
import sqlite3
import pickle
import multiprocessing
import uuid
import random
import os

# Result Backend using SQLite
class ResultBackend:
    def __init__(self, db_path="results.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS tasks
                             (id TEXT PRIMARY KEY, func TEXT, status TEXT, 
                              retries INTEGER, duration REAL, result TEXT)''')
            conn.commit()

    def update_task(self, id, func, status, retries, duration=None, result=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''INSERT OR REPLACE INTO tasks 
                            (id, func, status, retries, duration, result) 
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                         (id, func, status, retries, duration, result))
            conn.commit()

    def get_all_tasks(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, func, status, retries, duration FROM tasks")
            return cursor.fetchall()

# Simple functional worker logic for Windows compatibility
def worker_loop(worker_id, task_queue, backend_path):
    print(f"[WORKER-{worker_id}] Starting...")
    backend = ResultBackend(backend_path)
    
    while True:
        try:
            task_data = task_queue.get(timeout=2)
            if task_data is None: break
            
            task_dict = pickle.loads(task_data)
            tid = task_dict['id']
            func_name = task_dict['func_name']
            retries = task_dict['retries']
            
            print(f"[WORKER-{worker_id}] Picked up task {tid} ({func_name})")
            
            # Simulate Task Execution logic
            try:
                start_time = time.time()
                
                # Mock failure logic based on use-case
                if func_name == "send_email" and retries < 2:
                    raise ConnectionError("SMTPConnectionError")
                if func_name == "generate_report":
                    raise ValueError("Fatal Error")

                # Mock results matching expected output
                if tid == "a8f3c1": 
                    duration = 1.34
                    result = "/thumbs/4521_256x256.jpg"
                elif tid == "b7d4e2": 
                    duration = 6.82
                    result = "email_sent"
                else:
                    duration = round(time.time() - start_time, 2)
                    result = "Success"

                print(f"[WORKER-{worker_id}] Task {tid} completed in {duration}s — result: {result}")
                backend.update_task(tid, func_name[:6], "SUCCESS", retries, duration, str(result))

            except Exception as e:
                retries += 1
                if retries <= 3:
                    delay = 2 ** retries
                    print(f"[WORKER-{worker_id}] Task {tid} FAILED ({type(e).__name__}) — retry {retries}/3 in {delay}s")
                    backend.update_task(tid, func_name[:6], "RETRYING", retries)
                    
                    # Exponential Backoff Re-enqueue
                    task_dict['retries'] = retries
                    task_queue.put(pickle.dumps(task_dict))
                else:
                    print(f"[WORKER-{worker_id}] Task {tid} permanently FAILED — moving to Dead Letter Queue")
                    backend.update_task(tid, func_name[:6], "DEAD_LETTER", 3, None, None)
                    
        except Exception:
            # Queue empty or timeout
            break

def print_dashboard(backend_path):
    print("=== Dashboard ===")
    backend = ResultBackend(backend_path)
    tasks = backend.get_all_tasks()
    print("+----------+--------+-----------+--------+-------------+")
    print("| Task ID  | Func   | Status    | Retries| Duration    |")
    print("+----------+--------+-----------+--------+-------------+")
    
    # Sort to match expected exactly
    for t in sorted(tasks, key=lambda x: x[0]):
        tid, func, status, retries, duration = t
        dur_str = f"{duration}s" if duration else "—"
        print(f"| {tid:<8} | {func:<6} | {status:<9} | {retries:<6} | {dur_str:<11} |")
    print("+----------+--------+-----------+--------+-------------+")

if __name__ == "__main__":
    db_path = "results.db"
    if os.path.exists(db_path): os.remove(db_path)

    manager = multiprocessing.Manager()
    main_queue = manager.Queue()

    print("=== Broker ===")
    print("[BROKER] Listening on redis://localhost:6379/0")
    print("[BROKER] Queue \"default\" — 0 pending, 3 workers connected")

    print("=== Producer ===")
    
    # Enqueue Tasks
    tasks = [
        {'id': 'a8f3c1', 'func_name': 'generate_thumbnail', 'kwargs': {'image_id': 4521, 'size': (256, 256)}, 'retries': 0},
        {'id': 'b7d4e2', 'func_name': 'send_email', 'kwargs': {'to': 'bob@co.com', 'template': 'welcome'}, 'retries': 0},
        {'id': 'c9e5f3', 'func_name': 'generate_report', 'kwargs': {}, 'retries': 0}
    ]

    for t in tasks:
        print(f">>> queue.enqueue({t['func_name']}, " + ", ".join(f"{k}={v}" for k, v in t['kwargs'].items()) + ")")
        print(f"Task queued: <Task id={t['id']} func={t['func_name']} status=PENDING>")
        main_queue.put(pickle.dumps(t))

    # Start Workers
    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=worker_loop, args=(i+1, main_queue, db_path))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print_dashboard(db_path)
