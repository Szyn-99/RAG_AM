
install:
	-@pip install uv
	@uv sync


run:
	@uv run python3 -m src


debug:
	@uv run python3 -m pdb src/__main__.py


clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +


lint:
	uv run flake8 src
	uv run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs src


.PHONY: install run debug clean lint
