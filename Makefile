start-db:
	docker run --name local_mongo -d -p 27017:27017 mongo

stop-db:
	docker stop local_mongo || true
	docker rm local_mongo || true

run:
	uvicorn app.main:app --reload

test:
	PYTHONPATH=. pytest --maxfail=1 --disable-warnings -q