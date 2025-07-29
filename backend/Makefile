run:
	uv run uvicorn app.main:app --reload \
 		--port 8000

lint:
	uv run ruff check .

format:
	uv run ruff format app
	uv run ruff check --select I --fix app