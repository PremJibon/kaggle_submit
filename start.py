#!/usr/bin/env python3
"""Script to start the AI Personal Knowledge Assistant."""

import subprocess
import sys
import os
import time
import shutil


def start_backend():
    """Start the FastAPI backend."""
    print("Starting FastAPI backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return backend_process


def check_npm():
    """Check if npm is available."""
    return shutil.which("npm") is not None


def start_frontend():
    """Start the React frontend."""
    print("Starting React frontend...")
    frontend_process = subprocess.Popen(
        ["npm", "start"],
        cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    )
    return frontend_process


def main():
    """Main function to start the application."""
    print("=" * 50)
    print("AI Personal Knowledge Assistant")
    print("=" * 50)

    backend_process = None
    frontend_process = None

    try:
        # Start backend
        backend_process = start_backend()
        print("Backend started on http://localhost:8000")

        # Wait for backend to start
        time.sleep(3)

        # Check if npm is available before starting frontend
        if check_npm():
            try:
                frontend_process = start_frontend()
                print("Frontend started on http://localhost:3000")
            except Exception as e:
                print(f"Could not start frontend: {e}")
                frontend_process = None
        else:
            print("\nNote: npm/Node.js not found. React frontend not started.")
            print("Use the built-in web interface at http://localhost:8000")

        print("\n" + "=" * 50)
        print("Application is running!")
        print("=" * 50)
        print("\nAccess points:")
        print("  Web Interface:     http://localhost:8000")
        print("  API Documentation: http://localhost:8000/docs")
        print("  Interactive API:   http://localhost:8000/redoc")
        print("  Health Check:      http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the application")
        print("=" * 50)

        # Wait for backend process
        backend_process.wait()

    except KeyboardInterrupt:
        print("\n\nShutting down application...")

        if backend_process:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
            print("Backend stopped")

        if frontend_process:
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
            print("Frontend stopped")

        print("Application stopped successfully")

    except Exception as e:
        print(f"Error starting application: {e}")

        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()

        sys.exit(1)


if __name__ == "__main__":
    main()
