import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Copilot", layout="wide")

st.title("AI Data Pipeline Copilot 🚀")

user_input = st.text_input("Ask something:")

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

                data = response.json()

                # Intent
                st.markdown(f"🔎 **Intent:** `{data['intent']}`")

                # Agent Output
                st.markdown("### 🧠 Agent Output")

                output = data["agent_output"]

                if "message" in output:
                    st.write(output["message"])

                elif "root_cause" in output:
                    st.json(output)

                elif "design" in output:
                    st.write(output["design"])

                elif "generated_output" in output:
                    st.code(output["generated_output"])

                # Validation
                if "validation" in data:
                    st.markdown("### ✅ Validation")
                    st.json(data["validation"])

                # Decision
                if "decision" in data:
                    st.markdown("### ⚡ Decision")
                    st.json(data["decision"])

            except Exception as e:
                st.error(f"Error: {e}")
