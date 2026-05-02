start:
	docker-compose up

stop:
	docker-compose down

remove:
	docker-compose down -v --remove-orphans

build:
	docker-compose build

rebuild:
	make stop
	make build
	make start

test:
	docker compose run --rm \
		-e TEST_DATABASE_URL=postgresql://code_review_bot:changeme@postgres:5432/code_review_bot_test \
		fast-api pytest tests/ -v

test-cov:
	docker compose run --rm \
		-e TEST_DATABASE_URL=postgresql://code_review_bot:changeme@postgres:5432/code_review_bot_test \
		fast-api pytest tests/ -v --cov=. --cov-report=term-missing
