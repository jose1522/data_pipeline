from fastapi import FastAPI
from endpoints import v1

app = FastAPI(debug=True, title="Data API", version="1.0.0")
app.include_router(v1.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
