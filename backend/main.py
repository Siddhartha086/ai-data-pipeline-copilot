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
        return json.dumps(parsed)

    return json.dumps({
        "root_cause": "Parsing failed",
        "fix": raw,
        "confidence": 0.2,
        "impact": "unknown"
    })


# -----------------------------
# EXPLAIN AGENT
# -----------------------------
def explain_agent(question: str):
    prompt = f"""
    Explain clearly and concisely:

    {question}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.dumps({
        "message": res.choices[0].message.content.strip()
    })


# -----------------------------
# DESIGN AGENT
# -----------------------------
def design_agent(question: str):
    prompt = f"""
    You are a senior data architect.

    Provide a structured system design answer.

    Question: {question}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.dumps({
        "design": res.choices[0].message.content.strip()
    })


# -----------------------------
# GENERATE AGENT
# -----------------------------
def generate_agent(question: str):
    prompt = f"""
    Generate code or solution:

    {question}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.dumps({
        "generated_output": res.choices[0].message.content.strip()
    })


# -----------------------------
# VALIDATION AGENT
# -----------------------------
def validate_response(question: str, response: str):
    prompt = f"""
    Validate the AI response.

    ONLY return JSON.

    Format:
    {{
      "valid": true/false,
      "reason": "...",
      "safe_to_execute": true/false
    }}

    Question: {question}
    Response: {response}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = res.choices[0].message.content.strip()
    parsed = extract_json(raw)

    if parsed:
        return json.dumps(parsed)

    return json.dumps({
        "valid": True,
        "reason": "Fallback validation",
        "safe_to_execute": False
    })


# -----------------------------
# DECISION LAYER
# -----------------------------
def decision_layer(validation_json, agent_json):
    v = extract_json(validation_json)
    a = extract_json(agent_json)

    if not v or not a:
        return {
            "decision": "ERROR",
            "reason": "Parsing failure"
        }

    if not v.get("valid", False):
        return {
            "decision": "REJECTED",
            "reason": v.get("reason", "Invalid output")
        }

    if a.get("confidence", 0) > 0.8 and v.get("safe_to_execute", False):
        return {
            "decision": "AUTO_FIX",
            "action": a.get("fix", "")
        }

    return {
        "decision": "SUGGEST_ONLY",
        "fix": a.get("fix", "")
    }


# -----------------------------
# ROUTER
# -----------------------------
def route_query(intent: str, question: str):
    result = {"intent": intent}

    if "DEBUG" in intent:
        agent_output = debug_agent(question)
        validation = validate_response(question, agent_output)
        decision = decision_layer(validation, agent_output)

        result.update({
            "agent_output": agent_output,
            "validation": validation,
            "decision": decision
        })

    elif "EXPLAIN" in intent:
        result["agent_output"] = explain_agent(question)

    elif "DESIGN" in intent:
        result["agent_output"] = design_agent(question)

    elif "GENERATE" in intent:
        result["agent_output"] = generate_agent(question)

    else:
        result["agent_output"] = json.dumps({
            "message": "Unknown intent"
        })

    return result


# -----------------------------
# MAIN ENDPOINT
# -----------------------------
@app.post("/ask")
def ask(query: Query):
    try:
        question = query.question

        intent = classify_intent(question)

        result = route_query(intent, question)

        return result

    except Exception as e:
        return {
            "intent": "ERROR",
            "agent_output": json.dumps({
                "error": str(e)
            })
        }
