
import uvicorn
from fastapi import FastAPI
import multiprocessing

def create_app(name):
    app = FastAPI()
    @app.get("/")
    async def root():
        return {"service": name, "message": f"Hello from {name}"}
    
    @app.get("/latest")
    async def latest():
        return {"service": name, "data": f"Latest news from {name}"}
    return app

def run_app(name, port):
    app = create_app(name)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

if __name__ == "__main__":
    apps = [
        ("news-service", 4001),
        ("article-service", 4002),
        ("weather-service", 4003),
    ]
    
    processes = []
    print("Starting Local services on ports 4001, 4002, 4003...")
    
    try:
        for name, port in apps:
            p = multiprocessing.Process(target=run_app, args=(name, port))
            p.start()
            processes.append(p)
        
        print("All services are live. Press Ctrl+C to stop.")
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping services...")
        for p in processes:
            p.terminate()
