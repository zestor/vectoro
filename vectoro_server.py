from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from vectoro import vectoro

app = FastAPI()

vectoro = vectoro()

class AddVectorRequest(BaseModel):
    vector: List[float]
    text: str
    date: str

class SearchResult(BaseModel):
    text: str
    similarity: float
    date: str

@app.post("/save/")
async def save():
    vectoro.save_to_json()
    return {"message": "JSON saved successfully"}

@app.post("/vectors/")
async def add_vector(request: AddVectorRequest):
    vector = request.vector
    text = request.text
    date = request.date
    vectoro.add_vector(vector, text, date)
    return {"message": "Vector added successfully"}

@app.post("/search/")
async def search(query: str, top_k: int = 5):
    results = vectoro.search(query, top_k)
    return [SearchResult(text=result["text"], similarity=result["similarity"], date=result["date"]) for result in results]

# For local testing purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
