VERSION := $(or ${CI_COMMIT_SHORT_SHA},latest)

REPO=searturky/punch-service

build-local: 
	docker build -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .

build-image: 
	docker build -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .
	docker push $(REPO):$(VERSION)
	docker push $(REPO):latest
	docker rmi $(REPO):$(VERSION)

env-up:
	docker-compose -f docker/docker-compose-basic.yaml up -d

env-down:
	docker-compose -f docker/docker-compose-basic.yaml down

install:
	python -m pip install -r requirements.txt

start:
	dotenv run -- python -m uvicorn app.main:app --reload --reload-dir=app

lint:
	python -m pylint app/

test:
	python -m pytest tests/

clean-docker-pg-data:
	sudo rm -rf docker/data/postgresql