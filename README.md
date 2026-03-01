# Fintech Mini Bank

Mini banco fintech con arquitectura hexagonal:
- **API**: FastAPI
- **UI**: Streamlit
- **DB**: PostgreSQL (Docker)

La aplicación permite crear clientes y cuentas, ejecutar transacciones (depósito, retiro y transferencia) y consultar saldo/historial de transacciones.

---

## Requisitos
- Docker Desktop (Windows/Mac/Linux)
- Git (opcional, para clonar)

---

## Cómo correr

En la raíz del repositorio:

```bash
docker compose up --build
```

Cuando levante:
- **Swagger (API):** http://localhost:8000/docs
- **Streamlit (UI):** http://localhost:8501

Para detener:

```bash
docker compose down
```

---

## Cómo usar la UI (flujo recomendado)

1. Crear cliente (tab "Cliente")
2. Crear cuenta con el customer_id generado (tab "Cuenta")
3. Depositar a la cuenta (tab "Depósito")
4. Retirar o Transferir (tabs "Retiro" y "Transferencia")
5. Consultar cuenta/saldo (tab "Saldo")
6. Listar transacciones (tab "Transacciones")

---

## Endpoints principales (API)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /health | Healthcheck |
| POST | /customers | Crear cliente |
| POST | /accounts | Crear cuenta |
| GET | /accounts/{account_id} | Consultar cuenta/saldo |
| POST | /transactions/deposit | Depósito |
| POST | /transactions/withdraw | Retiro |
| POST | /transactions/transfer | Transferencia |
| GET | /accounts/{account_id}/transactions | Listar transacciones |

La documentación completa se puede ver en Swagger: http://localhost:8000/docs

---

## Decisiones de diseño

### Patrones aplicados

- **Facade**: `BankingFacade` como único punto de entrada desde la API hacia el dominio. Los endpoints no llaman servicios/repos directamente.
- **Strategy**: `FeeStrategy` (4 implementaciones: NoFee, Flat, Percent, Tiered) y `RiskStrategy` (3 implementaciones: MaxAmount, Velocity, DailyLimit) para reglas configurables.
- **Factory Method**: `TransactionFactory` crea objetos Transaction según tipo y valida campos requeridos.
- **Builder**: `TransactionBuilder` construye transacciones paso a paso con metadata.

### Arquitectura hexagonal

- `app/domain/` — Entidades, enums, excepciones, strategies, factories
- `app/services/` — Casos de uso (orquestación de flujo)
- `app/repositories/` — Interfaces (Protocol) + implementaciones ORM
- `app/application/` — FastAPI routes, DTOs, Facade
- `app/frontend/` — Streamlit (consume la API)

### Reglas de negocio

- **Fee**: Se aplica comisión del 1.5% (PercentFeeStrategy) a cada transacción
- **Risk**: Se valida monto máximo ($10,000), velocidad (máx 10 tx en 10 min), y límite diario ($50,000)
- **Estados**: Las cuentas FROZEN/CLOSED no pueden operar. Las transacciones se marcan APPROVED o REJECTED.

---

## Estructura del repositorio

```
app/
  domain/         — entidades, enums, excepciones, strategies, factories
  services/       — casos de uso
  repositories/   — interfaces + implementaciones ORM
  application/    — routes, DTOs, facade
  frontend/       — streamlit_app.py
tests/            — tests de dominio, strategies y API
docs/uml/         — diagramas UML (PlantUML)
docker-compose.yml
Dockerfile.api
Dockerfile.ui
```

---

## Tests

```bash
pytest tests/
```

- 2 tests de dominio (insufficient funds, cuenta frozen)
- 2 tests de strategies (fee calculation, risk rejection)
- 2 tests de API (deposit y transfer happy path)