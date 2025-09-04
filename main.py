import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Essalud API on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port)
