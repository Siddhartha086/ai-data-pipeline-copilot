import streamlit as st
import requests
import json

# Page config
st.set_page_config(page_title="AI Copilot", layout="wide")

st.title("AI Data Pipeline Copilot 🚀")

# Input
user_input = st.text_input("Ask something:")

# Button
if st.button("Send"):
    if not user_input.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking... 🤖"):
            try:
                response = requests.post(
                    "http://backend:8000/ask",
                    json={"question": user_input}
                )

                if response.status_code == 200:
                    data = response.json()

                    # ------------------------
                    # Intent
                    # ------------------------
                    st.markdown(f"### 🔍 Intent: `{data.get('intent', 'N/A')}`")

                    # ------------------------
                    # Agent Output
                    # ------------------------
                    if "agent_output" in data:
                        st.markdown("### 🧠 Agent Output")
                        try:
                            parsed = json.loads(data["agent_output"])
                            st.json(parsed)
                        except:
                            st.code(data["agent_output"])

                    # ------------------------
                    # Validation
                    # ------------------------
                    if "validation" in data:
                        st.markdown("### ✅ Validation")
                        try:
                            parsed = json.loads(data["validation"])
                            st.json(parsed)
                        except:
                            st.code(data["validation"])

                    # ------------------------
                    # Decision
                    # ------------------------
                    if "decision" in data:
                        st.markdown("### ⚡ Decision")
                        st.json(data["decision"])

                else:
                    st.error(f"Backend error: {response.status_code}")

            except Exception as e:
                st.error(f"Error: {e}")
