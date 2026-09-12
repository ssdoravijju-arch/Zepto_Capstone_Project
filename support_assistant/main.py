
import os
from pathlib import Path
from typing import TypedDict, Literal, List
import chromadb
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END

MOCK_LLM = os.getenv("MOCK_LLM","1") != "0"
DOCS_DIR = Path(__file__).parent/"docs"
CHROMA_DIR = Path(__file__).parent/"chroma_db"
KEYWORDS=["delivery","return","refund","membership","tracking","cancel","gift card","support hours"]

PROMPT_TEMPLATE="""ROLE:
You are Zepto's policy support assistant.
CONTEXT:
Use only the Zepto policy context provided below.
{context}
TASK:
Answer the customer's question accurately using the context.
FORMAT:
Return JSON with exactly: answer, sources, confidence.
LENGTH:
Keep the answer under 120 words.
NEGATIVE CONSTRAINT:
Do not answer using information not present in the provided context.
FEW-SHOT EXAMPLE:
Question: How long is a Zepto gift card valid?
Context: Gift cards are valid for 1 year from issue.
Answer: {{"answer":"Zepto gift cards are valid for 1 year from issue.","sources":["doc_07"],"confidence":1.0}}
CUSTOMER QUESTION:
{query}"""

embedder=SentenceTransformer("all-MiniLM-L6-v2")
client=chromadb.PersistentClient(path=str(CHROMA_DIR))
collection=client.get_or_create_collection("zepto_policies", metadata={"hnsw:space":"cosine"})

def ingest():
    if collection.count()>=8: return
    files=sorted(DOCS_DIR.glob("doc_*.txt"))
    docs=[f.read_text(encoding="utf-8") for f in files]
    ids=[f.stem for f in files]
    if collection.count():
        old=collection.get()
        if old.get("ids"): collection.delete(ids=old["ids"])
    embs=embedder.encode(docs, normalize_embeddings=True).tolist()
    collection.add(ids=ids, documents=docs, embeddings=embs,
                   metadatas=[{"source":i} for i in ids])
ingest()

class AskRequest(BaseModel):
    query:str=Field(min_length=1)

class AnswerResponse(BaseModel):
    answer:str
    sources:List[str]
    confidence:float=Field(ge=0,le=1)

class SupportState(TypedDict, total=False):
    query:str
    intent:Literal["policy_question","general_question"]
    answer:str
    sources:List[str]
    confidence:float
    retrieved_chunks:List[str]
    retrieved_ids:List[str]

def call_real_llm(prompt:str)->str:
    from groq import Groq
    key=os.getenv("GROQ_API_KEY")
    if not key: raise RuntimeError("GROQ_API_KEY required when MOCK_LLM=0")
    c=Groq(api_key=key)
    r=c.chat.completions.create(model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}],temperature=0)
    return r.choices[0].message.content

def validate_real(prompt:str)->AnswerResponse:
    last=None
    for _ in range(3):
        raw=call_real_llm(prompt)
        try:
            return AnswerResponse.model_validate_json(raw)
        except Exception as e:
            last=e
            prompt += "\nReturn ONLY valid JSON with answer, sources, confidence."
    return AnswerResponse(answer=f"ERROR: validation failed: {last}",sources=[],confidence=0.0)

def classify_intent(state:SupportState)->SupportState:
    q=state["query"]
    if MOCK_LLM:
        intent="policy_question" if any(k in q.lower() for k in KEYWORDS) else "general_question"
    else:
        raw=call_real_llm(f"Return only policy_question or general_question for: {q}").lower()
        intent="policy_question" if "policy_question" in raw else "general_question"
    return {**state,"intent":intent}

def retrieve_and_answer(state:SupportState)->SupportState:
    q=state["query"]
    qemb=embedder.encode([q],normalize_embeddings=True).tolist()
    r=collection.query(query_embeddings=qemb,n_results=3,include=["documents","metadatas","distances"])
    chunks=r["documents"][0]; ids=r["ids"][0]
    if MOCK_LLM:
        resp=AnswerResponse(answer=f"Based on the retrieved context: {chunks[0][:200]}",sources=ids,confidence=1.0)
    else:
        ctx="\n\n".join(f"[{i}] {c}" for i,c in zip(ids,chunks))
        resp=validate_real(PROMPT_TEMPLATE.format(context=ctx,query=q))
    return {**state,"retrieved_chunks":chunks,"retrieved_ids":ids,
            "answer":resp.answer,"sources":resp.sources,"confidence":resp.confidence}

def direct_answer(state:SupportState)->SupportState:
    if MOCK_LLM:
        resp=AnswerResponse(answer="I can only answer questions about Zepto policies right now.",sources=[],confidence=1.0)
    else:
        resp=validate_real(f'Answer briefly. Return ONLY JSON with answer, sources:[], confidence. Question: {state["query"]}')
    return {**state,"answer":resp.answer,"sources":resp.sources,"confidence":resp.confidence}

def route(state:SupportState)->str:
    return state["intent"]

b=StateGraph(SupportState)
b.add_node("classify_intent",classify_intent)
b.add_node("retrieve_and_answer",retrieve_and_answer)
b.add_node("direct_answer",direct_answer)
b.add_edge(START,"classify_intent")
b.add_conditional_edges("classify_intent",route,{
    "policy_question":"retrieve_and_answer",
    "general_question":"direct_answer"})
b.add_edge("retrieve_and_answer",END)
b.add_edge("direct_answer",END)
graph=b.compile()

app=FastAPI(title="Zepto Support Assistant")
@app.get("/")
def root():
    return {"service":"Zepto Support Assistant","mock_llm":MOCK_LLM,"collection_count":collection.count()}
@app.post("/ask",response_model=AnswerResponse)
def ask(req:AskRequest):
    r=graph.invoke({"query":req.query})
    return AnswerResponse(answer=r["answer"],sources=r["sources"],confidence=r["confidence"])
