run:
	uv run uvicorn app.main:app --reload \
 		--port 8000 \
		--ssl-keyfile=../certs/localhost-key.pem \
 		--ssl-certfile=../certs/localhost.pem

lint:
	uv run ruff check .

format:
	uv run ruff format app
	uv run ruff check --select I --fix app