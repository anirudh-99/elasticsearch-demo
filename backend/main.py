from config import INDEX_NAME
from utils import get_es_client
from pprint import pprint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from elastic_transport import ObjectApiResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/v1/search/")
async def search(search_query: str, skip: int=0, limit: int=10) -> dict:
    es = get_es_client(max_retries=5, sleep_time=5)
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": search_query,
                    "fields": ["title", "explanation"]
                }
            },
            "from": skip,
            "size": limit
        },
        filter_path=["hits.hits._source, hits.hits._score"]
    )
    hits = response["hits"]["hits"]
    return {"hits": hits}

@app.get("/api/v1/regular_search/")
async def regular_search(
    search_query: str,
    skip: int = 0,
    limit: int = 10,
    year: str | None = None,
    tokenizer: str = "Standard",
) -> dict:
    es = get_es_client()
    query = {
            "bool" : {
                "must": [
                    {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["title", "explanation"]
                        }
                    }
                ]
            }
        }
    
    if year:
        query["bool"]["filter"] = [
            {
                "range": {
                    "date": {
                        "gte": f"{year}-01-01",
                        "lte": f"{year}-12-31"
                    }
                }
            }
        ]

    response = es.search(
        index=INDEX_NAME,
        body={
            "query": query,
            "from": skip,
            "size": limit
        },
        filter_path=[
            "hits.hits._source",
            "hits.hits._score",
            "hits.total",
        ]
    )

    total_hits = get_total_hits(response)
    max_pages = calculate_max_pages(total_hits, limit)

    return {
            "hits": response["hits"].get("hits", []),
            "max_pages": max_pages,
        }

def get_total_hits(response: ObjectApiResponse) -> int:
    return response["hits"]["total"]["value"]


def calculate_max_pages(total_hits: int, limit: int) -> int:
    return (total_hits + limit - 1) // limit

@app.get("/api/v1/get_docs_per_year_count/")
async def get_docs_per_year_count(
    search_query: str, tokenizer: str = "Standard"
) -> dict:
    es = get_es_client()
    query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["title", "explanation"]
                        }
                    }
                ]
            }
        }
    
    response = es.search(index=INDEX_NAME, 
              body={
                  "query": query,
                    "aggs": {
                        "docs_per_year": {
                            "date_histogram": {
                                "field": "date",
                                "calendar_interval": "year",
                                "format": "yyyy"
                            }
                        }
                    }
              },
                filter_path=["aggregations.docs_per_year"]
            )
    return {"docs_per_year": extract_docs_per_year(response)}
    
def extract_docs_per_year(response: ObjectApiResponse) -> dict:
    aggregations = response.get("aggregations", {})
    docs_per_year = aggregations.get("docs_per_year", {})
    buckets = docs_per_year.get("buckets", [])
    return {bucket["key_as_string"]: bucket["doc_count"] for bucket in buckets}

