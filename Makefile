run-dev:
	uvicorn app.main:app --reload --log-level debug
install-req:
	pip install -r requirements.txt
migrate-gen:
	alembic revision --autogenerate -m "$(msg)"
migrate-apply:
	alembic upgrade head