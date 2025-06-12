pip install uv

uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

uv add tensorflow
uv sync

uv run task dev 