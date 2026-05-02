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
	docker compose run --rm fast-api pytest
