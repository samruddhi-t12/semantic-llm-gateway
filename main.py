from fastapi import FastAPI, HTTPException
import asyncio
import random

app = FastAPI(title="University Result Portal API")

@app.get("/")
def read_root():
    return {"message": "Result Portal is LIVE. Good luck."}

@app.get("/result/{seat_number}")
async def get_result(seat_number: str):
    # Simulating a slow, heavy database query searching for the student
    await asyncio.sleep(0.8) 
    
    # Under heavy load, databases randomly drop connections. 
    # We simulate a 5% chance of the database timing out to make our tests realistic!
    if random.random() < 0.05:
        raise HTTPException(status_code=503, detail="Database Connection Timeout. Please try again.")

    # Generate a random CGPA for the simulation
    cgpa = round(random.uniform(6.0, 9.8), 2)
    return {
        "seat_number": seat_number,
        "status": "PASS" if cgpa > 6.5 else "PROMOTED",
        "cgpa": cgpa,
        "message": "Data retrieved successfully."
    }