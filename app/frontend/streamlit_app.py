import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 15

st.set_page_config(page_title="Fintech Mini Bank", layout="wide")
st.title("Fintech Mini Bank")

def post(path: str, payload: dict):
    r = requests.post(f"{API_URL}{path}", json=payload, timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"detail": r.text}
    return r.status_code, data

def get(path: str):
    r = requests.get(f"{API_URL}{path}", timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"detail": r.text}
    return r.status_code, data

tabs = st.tabs(["Cliente", "Cuenta", "Deposito", "Retiro", "Transferencia", "Saldo", "Transacciones"])

with tabs[0]:
    st.subheader("Crear cliente")
    name = st.text_input("Nombre")
    email = st.text_input("Email")
    if st.button("Crear cliente", type="primary"):
        code, data = post("/customers", {"name": name, "email": email})
        if code == 200:
            st.success(f"Cliente creado con ID: {data.get('id')}")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)

with tabs[1]:
    st.subheader("Crear cuenta")
    customer_id = st.text_input("Customer ID")
    currency = st.text_input("Currency", value="USD")
    if st.button("Crear cuenta", type="primary"):
        code, data = post("/accounts", {"customer_id": customer_id, "currency": currency})
        if code == 200:
            st.success(f"Cuenta creada con ID: {data.get('id')}")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)

with tabs[2]:
    st.subheader("Deposito")
    dep_account_id = st.text_input("Account ID", key="dep_acc")
    dep_amount = st.number_input("Monto", min_value=0.01, step=10.0, key="dep_amt")
    if st.button("Depositar", type="primary"):
        code, data = post("/transactions/deposit", {"account_id": dep_account_id, "amount": float(dep_amount)})
        if code == 200:
            st.success("Deposito exitoso")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)

with tabs[3]:
    st.subheader("Retiro")
    wit_account_id = st.text_input("Account ID", key="wit_acc")
    wit_amount = st.number_input("Monto", min_value=0.01, step=10.0, key="wit_amt")
    if st.button("Retirar", type="primary"):
        code, data = post("/transactions/withdraw", {"account_id": wit_account_id, "amount": float(wit_amount)})
        if code == 200:
            st.success("Retiro exitoso")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)

with tabs[4]:
    st.subheader("Transferencia")
    from_id = st.text_input("From account")
    to_id = st.text_input("To account")
    tr_amount = st.number_input("Monto", min_value=0.01, step=10.0, key="tr_amt")
    if st.button("Transferir", type="primary"):
        code, data = post(
            "/transactions/transfer",
            {"from_account_id": from_id, "to_account_id": to_id, "amount": float(tr_amount)}
        )
        if code == 200:
            st.success("Transferencia exitosa")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)

with tabs[5]:
    st.subheader("Ver saldo / cuenta")
    get_account_id = st.text_input("Account ID", key="get_acc")
    if st.button("Consultar", type="primary"):
        code, data = get(f"/accounts/{get_account_id}")
        if code == 200:
            st.success(f"Balance: ${data.get('balance', 0):.2f}")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)

with tabs[6]:
    st.subheader("Listar transacciones")
    tx_account_id = st.text_input("Account ID", key="tx_acc")
    if st.button("Listar", type="primary"):
        code, data = get(f"/accounts/{tx_account_id}/transactions")
        if code == 200:
            st.success(f"Total: {data.get('total_count', 0)} transacciones")
        else:
            st.error(data.get("detail", "Error"))
        st.json(data)