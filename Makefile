.PHONY: clean
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -f .coverage

.PHONY: destroy
destroy:
	docker-compose down

.PHONY: lint
lint:
	docker-compose run --rm pdf-agent-test sh -c " \
	    flake8 . && \
	    isort --check --diff . && \
		mypy pdf_agent/"

.PHONY: refreeze
refreeze:
	bash bin/refreeze.sh

.PHONY: run
run:
	docker-compose up pdf-agent

.PHONY: build
build:
	docker-compose build pdf-agent

.PHONY: test
test:
	docker-compose run --rm pdf-agent-test

.PHONY: coverage
coverage:
	docker-compose run --rm pdf-agent-test sh -c " \
		coverage run -m pytest --durations=10 && \
		coverage report -m "

.PHONY: alembic-version
alembic-version:
	docker-compose run --rm pdf-agent sh -c " \
	    alembic revision --autogenerate -m \"${msg}\""