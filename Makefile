run-dev:
	uvicorn app.main:app --log-level debug --workers 4
test:
	@python -m unittest discover -s tests
install-req:
	pip install -r requirements.txt
migrate-gen:
	alembic revision --autogenerate -m "$(msg)"
migrate-apply:
	alembic upgrade head
