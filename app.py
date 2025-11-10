import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import recommend_assessments


port = int(os.environ.get("PORT", 8002))
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    job_description: str

@app.get("/")
def read_root():
    return {"message": "SHL Backend is running!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.post("/recommend")
async def recommend(request: JobRequest):
    """
    Assessment Recommendation Endpoint
    
    Accepts a job description or natural language query and returns 
    recommended relevant assessments (5-10 recommendations).
    
    Response format:
    {
        "recommendations": [
            {
                "name": "Assessment Name",
                "url": "https://www.shl.com/..."
            },
            ...
        ]
    }
    """
    try:
        recommendations = await recommend_assessments(request.job_description)
        
        # Ensure we have at least 1 recommendation (assignment says minimum 1, but we aim for 5-10)
        if not recommendations:
            return {
                "recommendations": [],
                "message": "No recommendations found. Please try a more detailed job description."
            }
        
        return {"recommendations": recommendations}
    except Exception as e:
        return {
            "recommendations": [],
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)