# Fintech Mini Bank

Mini banco fintech con arquitectura por capas:
- **API**: FastAPI
- **UI**: Streamlit
- **DB**: PostgreSQL (Docker)

La aplicación permite crear clientes y cuentas, ejecutar transacciones (depósito, retiro y transferencia) y consultar saldo/historial de transacciones.

---

## Requisitos
- Docker Desktop (Windows/Mac/Linux)
- Git (opcional, para clonar)

---

## Cómo correr (Docker)

En la raíz del repositorio:

```bash
docker compose up --build

Cuando levante:
Swagger (API): http://localhost:8000/docs
Streamlit (UI): http://localhost:8501

Para detener:
docker compose down

Cómo usar la UI (flujo recomendado)

Crear cliente (tab “Cliente”)

Crear cuenta con el customer_id generado (tab “Cuenta”)

Depositar a la cuenta (tab “Depósito”)

Retirar o Transferir (tabs “Retiro” y “Transferencia”)

Consultar cuenta/saldo (tab “Saldo”)

Listar transacciones (tab “Transacciones”)

Endpoints principales (API)

GET /health — healthcheck

POST /customers — crear cliente

POST /accounts — crear cuenta

GET /accounts/{account_id} — consultar cuenta/saldo

POST /transactions/deposit — depósito

POST /transactions/withdraw — retiro

POST /transactions/transfer — transferencia

GET /accounts/{account_id}/transactions — listar transacciones

Nota: La documentación completa y los esquemas se pueden ver en Swagger: http://localhost:8000/docs

Decisiones de diseño

Facade: se plantea un único punto de entrada (BankingFacade) para orquestar casos de uso (crear cliente/cuenta y transacciones).

Strategy: uso de estrategias para cálculo de comisiones (FeeStrategy) y reglas de riesgo (RiskStrategy).

Repositorios: separación entre lógica de negocio y persistencia (PostgreSQL/SQLAlchemy) mediante repositorios.

Estructura del repositorio

app/ — FastAPI + capa de aplicación

app/application/ — rutas y DTOs

app/frontend/ — Streamlit UI (streamlit_app.py)

docs/ — documentación UML (PlantUML)

docker-compose.yml — orquestación (db + api + ui)

Dockerfile.api — contenedor de la API

Dockerfile.ui — contenedor de la UI
