import streamlit as st

def metric_cards(metrics):
    cols = st.columns(min(4, max(1, len(metrics))))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label, value)

def alert_card(alert):
    st.warning(f"{alert.get('event')} — {alert.get('location')}")
    st.write(alert.get("english",""))
    st.write(alert.get("tamil",""))

def qaoa_status(result):
    st.write(f"**{result.get('method')}** — {result.get('status')}")
    st.write({"p": result.get("p"), "circuit_depth": result.get("circuit_depth"),
              "execution_time": result.get("execution_time"), "best_bitstring": result.get("best_bitstring")})

def emergency_status(em):
    if em:
        st.info(f"{em.get('corridor_status')} — {em.get('clearance_status')}: {em.get('reason')}")

def signal_table(plans):
    st.table([{"Junction": j, "Optimized plan": p} for j,p in plans.items()])

def explanation_card(text):
    st.success(text)
