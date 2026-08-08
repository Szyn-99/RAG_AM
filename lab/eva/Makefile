.PHONY: install run debug clean lint lint-strict

install:
	UV_CACHE_DIR="$$HOME/goinfre" \
	UV_PROJECT_ENVIRONMENT="$$HOME/goinfre/rag-venv" \
	UV_LINK_MODE=copy \
	uv sync

run:
	HF_HOME="$$HOME/goinfre" \
	UV_PROJECT_ENVIRONMENT="$$HOME/goinfre/rag-venv" \
	uv run python3 -m src $(ARG)
debug:
	HF_HOME="$$HOME/goinfre" \
	UV_PROJECT_ENVIRONMENT="$$HOME/goinfre/rag-venv" \
	uv run python3 -m pdb -m src $(ARG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +


lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict