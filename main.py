# main.py
import uvicorn

if __name__ == "__main__":
    # This tells the Uvicorn server to find the 'app' object inside the 'backend.app' module.
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000,reload=True)