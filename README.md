# 🚀 Agentic AI Data Pipeline Copilot — Mark 1

An enterprise-style AI system that detects, diagnoses, and suggests fixes for data pipeline failures using multi-agent reasoning.

---

## 🧠 Features

- 🔍 Intent classification (DEBUG / DESIGN / EXPLAIN / GENERATE)
- 🧠 Multi-agent architecture
- ✅ Validation layer (checks correctness & safety)
- ⚡ Decision engine (AUTO_FIX / SUGGEST_ONLY)
- 🐳 Docker-based deployment
- ☁️ AWS-ready architecture

---

## 🏗 Architecture

User → Streamlit UI → FastAPI Backend → Agent System → LLM → Response


---

## ⚙️ Run Locally

```bash
docker compose up --build

Access:

Frontend: http://localhost:8501
Backend: http://localhost:8000


📌 Example Output
Root cause detection
Suggested fix
Confidence score
Business impact
Automated decision
🚀 Roadmap
 RAG integration (past failures memory)
 Snowflake integration (real query context)
 Execution engine (auto-fix pipelines)
 Monitoring & observability
👨‍💻 Author

Siddhartha Nath
