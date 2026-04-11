# Real-Time Data Streaming & Anomaly Detection System

A asynchronous system designed to ingest, process, and analyze live IoT sensor data using a headless WebSocket architecture. The system computes real-time statistics (Moving Averages, Z-Scores) and triggers automated alerts based on configurable thresholds.

## 🚀 Key Features

- **Live Stream Ingestion**: Decoupled client-server architecture using WebSockets for low-latency data streaming.
- **Windowed Aggregations**: Uses `pandas` and `deque` to maintain a sliding window of historical data for real-time analysis.
- **Anomaly Detection**: Implements Z-Score calculations (`(value - mean) / std_dev`) to detect statistical outliers in sensor readings.
- **Event-Driven Alerts**: Automated console alerting for critical thresholds (e.g., Temperature > 100°F).
- **Asynchronous Core**: Built on `asyncio` and `FastAPI` for concurrent handling of multiple data feeds.

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (Asynchronous Web Framework)
- **Data Processing**: Pandas, NumPy
- **Communication**: WebSockets (via `websockets` and `starlette`)
- **Simulation**: Custom Async Generator (Simulator)

## Project Structure

```text
task-8/
├── main.py         # Headless WebSocket Server & Processor
├── client.py       # Asynchronous Sensor Simulator (Client)
├── processor.py    # Statistical Analysis Logic (Moving Avg, Z-Score)
└── README.md       # Project Documentation
```

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   cd task-8
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8+ installed, then run:
   ```bash
   pip install fastapi uvicorn pandas websockets numpy
   ```

## 🏃 How to Run

You will need two terminal windows:

### 1. Start the Server
```bash
python main.py
```
*The server will listen on `ws://localhost:8000/ws` for incoming sensor data.*

### 2. Start the Client
```bash
python client.py
```
*The client will connect to the server and begin streaming simulated temperature and vibration data.*

## 📝 Example Output

### Client Console:
```text
[CLIENT] Connecting to ws://localhost:8000/ws...
[CLIENT] Connection established. Sending data...
```

### Server Console:
```text
=== Server Console ===
[INFO] Stream processor started — ready for sensor feed
[INFO] Application running on http://localhost:8000
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     ('127.0.0.1', 49346) - "WebSocket /ws" [accepted] 
[INFO] Client connected — starting live processing
INFO:     connection open
[22:05:06] sensor-T1 temp=72.0F vibration=0.14g status=NORMAL
[22:05:07] sensor-T1 temp=73.0F vibration=0.11g status=NORMAL
[22:05:08] sensor-T1 temp=73.5F vibration=0.10g status=NORMAL
[22:05:09] sensor-T1 temp=71.7F vibration=0.12g status=NORMAL

=== Alert Triggered ===
[ALERT] sensor-T1 — Temperature exceeded threshold (>100F)  
Current: 101.4F | 5-min avg: 73.2F | Deviation: 4.8 sigma   
Action: Notification sent to ops-team@factory.com
=======================
```

## ⚠️ Important Notes & Limitations

- **Headless Design**: This version focuses on console-based processing for maximum performance and stability.
- **Window Size**: The default window for moving averages is 60 samples (approx. 1 minute at a 1s interval).
- **Z-Score Sensitivity**: Anomalies are flagged at `|Z| > 3.0`. This can be adjusted in `processor.py`.

## 🔮 Future Improvements

- **Database Persistence**: Store anomalies in SQLite or Postgres for historical auditing.
- **Multi-Sensor scaling**: Support for hundreds of concurrent sensor connections.
- **External Notifications**: Integrate with SendGrid or Slack API for real-world alerting.
- **Dashboard API**: Add REST endpoints to query the current state of sensors.
