install:
	uv sync


run:
	uv run -m pacman.main pacman/confic_loader.json



clean:
	rm -rf __pycache__ .mypy_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
