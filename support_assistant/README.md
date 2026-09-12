# Module 3 - Support Assistant

## Architecture
Ingestion -> Embedding -> Retrieval -> Generation

- Ingestion: `main.py::ingest()` loads all 8 files from `docs/`.
- Embedding: `all-MiniLM-L6-v2` creates local embeddings.
- Storage: ChromaDB collection `zepto_policies` stores the vectors using cosine similarity.
- Routing: LangGraph `classify_intent` sends policy questions to `retrieve_and_answer`, otherwise to `direct_answer`.
- Retrieval: `retrieve_and_answer` fetches top-3 chunks.
- Generation: default `MOCK_LLM=1` uses deterministic canned responses. Optional `MOCK_LLM=0` uses the structured prompt and real LLM.
- Real-LLM output is Pydantic-validated and retried up to 2 additional times.

## Prompt
The structured prompt in `main.py` contains role, context, task, format, length, a negative constraint, and a few-shot example.

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

## Example 1 - policy question
Request:
```bash
curl -X POST http://127.0.0.1:7860/ask -H "Content-Type: application/json" -d "{"query":"What is the delivery fee for a small order?"}"
```

Example JSON:
```json
{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard delivery is","sources":["doc_01","doc_03","doc_05"],"confidence":1.0}
```

## Example 2 - general question
Request:
```bash
curl -X POST http://127.0.0.1:7860/ask -H "Content-Type: application/json" -d "{"query":"Who won the football match yesterday?"}"
```

JSON:
```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

## Docker
```bash
docker build -t zepto-support .
docker run --rm -p 7860:7860 zepto-support
```

Optional real LLM:
```bash
set MOCK_LLM=0
set GROQ_API_KEY=your_key
uvicorn main:app --port 7860
```
