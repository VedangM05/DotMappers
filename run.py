import sys
import os
import argparse
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Support Ticket System — DOTMappers Assessment Runner")
    parser.add_argument("--mode", choices=["all", "api", "ui"], default="all", help="Service mode to start")
    parser.add_argument("--api-port", type=int, default=8000, help="FastAPI port")
    parser.add_argument("--ui-port", type=int, default=8501, help="Streamlit UI port")
    args = parser.parse_args()

    # Ensure database initialization
    logger.info("Initializing Database & Embeddings...")
    from src.database import db
    logger.info("Database Ready.")

    processes = []
    
    try:
        # Check venv python executable
        venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python")
        python_cmd = venv_python if os.path.exists(venv_python) else sys.executable
        
        venv_uvicorn = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "uvicorn")
        uvicorn_cmd = venv_uvicorn if os.path.exists(venv_uvicorn) else "uvicorn"

        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

        if args.mode in ["all", "api"]:
            logger.info(f"Starting FastAPI server on http://localhost:{args.api_port}...")
            api_proc = subprocess.Popen([
                uvicorn_cmd, "src.api:app", "--host", "0.0.0.0", "--port", str(args.api_port), "--reload"
            ])
            processes.append(api_proc)

        if args.mode in ["all", "ui"]:
            time.sleep(1)
            logger.info(f"Starting Vite React UI on http://localhost:{args.ui_port}...")
            ui_proc = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", str(args.ui_port), "--host"],
                cwd=frontend_dir
            )
            processes.append(ui_proc)

        logger.info("System fully online!")
        logger.info(f"• OpenAPI REST Docs: http://localhost:{args.api_port}/docs")
        logger.info(f"• React Web UI:      http://localhost:{args.ui_port}")

        # Keep running
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        logger.info("Shutting down processes...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
