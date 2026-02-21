from fastapi import FastAPI, UploadFile, File, HTTPException
from app.engine import PortfolioEngine
import shutil
import os
import tempfile

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "System Online"}


# Note: "async" is needed because file uploads are an asynchronous operation
@app.post("/analyze")
async def analyze_portfolio(file: UploadFile = File(...)):
    """
    Accepts a CSV file, calculates volatility, and returns the risk score.
    """
    temp_filename = "temp_upload.csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_filename = tmp.name 
    try:
        with open(temp_filename, "wb") as f:
            shutil.copyfileobj(file.file, f)
        engine = PortfolioEngine(temp_filename)
        engine.load_portfolio()
        prices = engine.get_price_history()
        risk = engine.calculate_volatility(prices)
        os.remove(temp_filename)
        

        return {
            "risk_score": risk,
            "formatted": f"{risk*100:.2f}%",
            "rating": "HighRisk" if risk > 0.2 else "ModerateRisk"
        }

    except Exception as e:
        # If anything breaks (bad CSV, yfinance down), tell the user
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return {"error": str(e)}