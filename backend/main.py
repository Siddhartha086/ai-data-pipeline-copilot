from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import re
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# REQUEST MODEL
# -----------------------------
class Query(BaseModel):
    question: str


# -----------------------------
# SAFE JSON EXTRACTOR
# -----------------------------
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None
    return None


# -----------------------------
# INTENT CLASSIFIER
# -----------------------------
def classify_intent(question: str) -> str:
    prompt = f"""
    Classify the query into one of:
    DEBUG, DESIGN, EXPLAIN, GENERATE

    Return ONLY one word.

    Query: {question}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content.strip().upper()


# -----------------------------
# DEBUG AGENT
# -----------------------------
def debug_agent(question: str):
    prompt = f"""
    You are a senior data engineer.

    STRICTLY return VALID JSON ONLY.

    Format:
    {{
      "root_cause": "...",
      "fix": "...",
      "confidence": 0.0,
      "impact": "low/medium/high"
    }}

    Question: {question}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = res.choices[0].message.content.strip()
    parsed = extract_json(raw)

    if parsed:
        return parsed

    return {
        "root_cause": "Parsing failed",
        "fix": raw,
        "confidence": 0.2,
        "impact": "unknown"
    }


# -----------------------------
# EXPLAIN AGENT
# -----------------------------
def explain_agent(question: str):
    prompt = f"Explain clearly:\n{question}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "message": res.choices[0].message.content.strip()
    }


# -----------------------------
# DESIGN AGENT
# -----------------------------
def design_agent(question: str):
    prompt = f"You are a system architect. Design solution:\n{question}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "design": res.choices[0].message.content.strip()
    }


# -----------------------------
# GENERATE AGENT
# -----------------------------
def generate_agent(question: str):
    prompt = f"Generate code/solution:\n{question}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "generated_output": res.choices[0].message.content.strip()
    }


# -----------------------------
# VALIDATION
# -----------------------------
def validate_response(question: str, response: dict):
    prompt = f"""
    Validate response.

    Return JSON:
    {{
      "valid": true/false,
      "safe_to_execute": true/false
    }}

    Question: {question}
    Response: {response}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    parsed = extract_json(res.choices[0].message.content.strip())

    if parsed:
        return parsed

    return {"valid": True, "safe_to_execute": False}


# -----------------------------
# DECISION
# -----------------------------
def decision_layer(validation, agent_output):
    if not validation.get("valid"):
        return {"decision": "REJECTED"}

    if agent_output.get("confidence", 0) > 0.8 and validation.get("safe_to_execute"):
        return {"decision": "AUTO_FIX"}

    return {"decision": "SUGGEST_ONLY"}


# -----------------------------
# ROUTER
# -----------------------------
def route_query(intent, question):
    result = {"intent": intent}

    if intent == "DEBUG":
        agent_output = debug_agent(question)
        validation = validate_response(question, agent_output)
        decision = decision_layer(validation, agent_output)

        result.update({
            "agent_output": agent_output,
            "validation": validation,
            "decision": decision
        })

    elif intent == "EXPLAIN":
        result["agent_output"] = explain_agent(question)

    elif intent == "DESIGN":
        result["agent_output"] = design_agent(question)

    elif intent == "GENERATE":
        result["agent_output"] = generate_agent(question)

    else:
        result["agent_output"] = {"message": "Unknown intent"}

    return result


# -----------------------------
# API
# -----------------------------
@app.post("/ask")
def ask(query: Query):
    intent = classify_intent(query.question)
    return route_query(intent, query.question)
