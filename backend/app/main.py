from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .lib.utils import get_domain, get_product_id, summarize_reviews
from .lib.scrape_amazon.scraper import get_reviews
from .lib.s3 import download_file
from .lib.classifier import get_feature_vector, pre_process, classify_many
from .lib.selenium_scraper import AmazonScraper
from mangum import Mangum

import pandas as pd
import os
import pickle
import nltk

load_dotenv()
app = FastAPI()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class AnalyzeRequest(BaseModel):
    url: str
    token: str


@app.on_event("startup")
def server_startup():
    global classifier
    classifier_path = download_file("reviewpulse", "models/classifier.pkl", "/tmp")
    with open(classifier_path, "rb") as f:
        classifier = pickle.load(f)

    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("averaged_perceptron_tagger")

    print("Startup complete!")


@app.post("/v1/analyze")
def analyze(request: AnalyzeRequest):
    try:
        token = request.token
        scraper = AmazonScraper(request.url, token)
        df = scraper.scrape_reviews(page_limit=10)

        print(f"Num of reviews = {str(len(df))}")

        fvs = []
        for i in range(len(df)):
            row = df.iloc[i]
            fv = get_feature_vector(
                row.rating, row.verified_purchase, pre_process(row.review_text)
            )
            fvs.append(fv)

        preds = classify_many(fvs, classifier)
        df["prediction"] = preds

        num_real_reviews = df[df["prediction"] == "real"].shape[0]
        num_fake_reviews = df[df["prediction"] == "fake"].shape[0]
        average_real_rating = df[df["prediction"] == "real"]["rating"].mean()

        reviews = df["review_text"].to_list()
        summary = summarize_reviews(reviews)

        response_data = {
            "num_sampled": len(df),
            "num_real_reviews": num_real_reviews,
            "num_fake_reviews": num_fake_reviews,
            "average_real_rating": round(average_real_rating, 2),
            "summary": summary,
        }

        return JSONResponse({"success": True, "data": response_data})
    except Exception as e:
        print(e)
        return JSONResponse(
            {
                "success": False,
                "message": "Internal server error. Please try again after some time",
            },
            status_code=500,
        )


lambda_handler = Mangum(app)
