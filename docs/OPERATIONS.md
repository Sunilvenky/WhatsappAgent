# Operations notes (PR1)

## Start dev stack:
```bash
./dev.sh up
```

## Stop dev stack:
```bash
./dev.sh down
```

## Services:
- **API**: Default exposed on http://localhost:3000
- **LLM stub**: Default exposed on http://localhost:4000/v1/complete
- **Postgres**: localhost:5432
- **Redis**: localhost:6379
- **MinIO**: http://localhost:9000
- **Adminer**: http://localhost:8080

## Running the API locally:
```bash
# From repo root
python -m apps.api.app.main
```

## Running tests:
```bash
pip install -r requirements.txt
pytest -q
```