import streamlit as st
import json
import os
import pandas as pd

LEDGER_FILE = os.path.join(os.path.dirname(__file__), "token_ledger.json")

st.set_page_config(page_title="Turtle-DB Token Monitor", page_icon="🐢", layout="wide")

st.title("🛡️ Token Weight Monitor")
st.markdown("Real-time visibility into the Vision-First QA budget.")

def load_data():
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    return None

data = load_data()

if data:
    # Top Level Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Weight (Tokens)", f"{data['total_weight']:,}")
    col2.metric("Estimated Cost", f"${data['total_cost']:,.4f}")
    col3.metric("Total Interactions", len(data["entries"]))

    # Detailed Table
    st.subheader("📜 Interaction Ledger")
    df = pd.DataFrame(data["entries"])
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime('%H:%M:%S')
        st.dataframe(df, use_container_width=True)

        # Charts
        st.subheader("📊 Usage by Model")
        model_counts = df.groupby("model")["input"].sum().reset_index()
        st.bar_chart(model_counts.set_index("model"))
    else:
        st.info("No entries recorded yet.")
else:
    st.warning("Token ledger not found. Initialize a task to see data.")

if st.button("🔄 Refresh Data"):
    st.rerun()
