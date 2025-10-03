from fastapi import FastAPI
from api.routes_job import router as job_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello Job Matcher!"}

# Gắn router cho Job API
app.include_router(job_router)
