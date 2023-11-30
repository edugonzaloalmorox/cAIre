from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openai
from fastapi import FastAPI, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer



from config import (
    COLLECTION_NAME,
    OPENAI_API_KEY,
    QDRANT_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
)

openai.api_key = OPENAI_API_KEY

qdrant_client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
    api_key=QDRANT_API_KEY,
)

retrieval_model = SentenceTransformer("msmarco-MiniLM-L-6-v3")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")


def build_prompt(question: str, reviews: list) -> tuple[str, str]:
    prompt = f"""
    Type a question: '{question}'

    You've selected the most relevant reviews. Cite summaries of them in your answer:

    """
    return prompt


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/ask")
def ask(question:str):
    try:
        similar_docs = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=retrieval_model.encode(question),
            limit=3,
            append_payload=True,
        )

        prompt = build_prompt(question, similar_docs)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.2,
        )

        result = response["choices"][0]['message']['content']

        # Log the result for debugging
        print("Result:", result)

        return {"response": result}

    except Exception as e:
        # Log the exception for debugging
        print("Exception:", str(e))
        raise HTTPException(status_code=422, detail=str(e))



