# Quick Launch script for Agent Riley
import subprocess
import sys
import time

def run():
    print("=" * 60)
    print("  TASK FORCE 141 - AGENT RILEY LOCAL DEPLOYMENT SYSTEM")
    print("=" * 60)
    print("[1/2] Launching Tactical Backend (FastAPI on http://localhost:8000)...")
    backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    
    time.sleep(2)
    print("[2/2] Launching Dark Neumorphic Tactical UI (Streamlit on http://localhost:8501)...")
    frontend = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app/views/streamlit_app.py", "--server.port", "8501"])

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n[MISSION ABORT] Shutting down tactical servers...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    run()
