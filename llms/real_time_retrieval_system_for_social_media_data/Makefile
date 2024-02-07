install:
	poetry install

run:
	RUST_BACKTRACE=1 poetry run python -m bytewax.run ingest:flow

run_qdrant_as_docker:
	docker run -d -p 6333:6333 -v $(CURDIR)/qdrant_storage:/qdrant/storage qdrant/qdrant