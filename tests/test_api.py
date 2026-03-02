import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_deposit_happy_path():
    # Crear cliente
    res = client.post("/customers", json={"name": "Test User", "email": "test_deposit@example.com"})
    assert res.status_code == 200
    customer_id = res.json()["id"]

    # Crear cuenta
    res = client.post("/accounts", json={"customer_id": customer_id, "currency": "USD"})
    assert res.status_code == 200
    account_id = res.json()["id"]

    # Depositar
    res = client.post("/transactions/deposit", json={"account_id": account_id, "amount": 500.0})
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "DEPOSIT"
    assert data["status"] == "APPROVED"
    assert data["amount"] == 500.0

    # Verificar saldo (500 - 1.5% fee = 492.50)
    res = client.get(f"/accounts/{account_id}")
    assert res.status_code == 200
    assert res.json()["balance"] == 492.5


def test_transfer_happy_path():
    # Crear cliente
    res = client.post("/customers", json={"name": "Sender", "email": "sender_transfer@example.com"})
    sender_id = res.json()["id"]

    res = client.post("/customers", json={"name": "Receiver", "email": "receiver_transfer@example.com"})
    receiver_id = res.json()["id"]

    # Crear cuentas
    res = client.post("/accounts", json={"customer_id": sender_id, "currency": "USD"})
    from_account = res.json()["id"]

    res = client.post("/accounts", json={"customer_id": receiver_id, "currency": "USD"})
    to_account = res.json()["id"]

    # Depositar en cuenta origen
    client.post("/transactions/deposit", json={"account_id": from_account, "amount": 1000.0})

    # Transferir
    res = client.post("/transactions/transfer", json={
        "from_account_id": from_account,
        "to_account_id": to_account,
        "amount": 200.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "TRANSFER"
    assert data["status"] == "APPROVED"

    # Verificar que el receptor recibió 200
    res = client.get(f"/accounts/{to_account}")
    assert res.json()["balance"] == 200.0