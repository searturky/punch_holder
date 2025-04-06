VERSION := $(or ${CI_COMMIT_SHORT_SHA},latest)

REPO := $(or ${CI_REGISTRY_IMAGE}, registry.searturky.cn/ops/clockin)
DOCKER_HUB := $(or ${CI_REGISTRY}, searturky/punch-service)

build-local: 
	docker build -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .

build-image: 
	docker build -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .
	docker push $(REPO):$(VERSION)
	docker push $(REPO):latest
	docker rmi $(REPO):$(VERSION)

build-image-dockerhub: 
	docker build -t $(DOCKER_HUB):$(VERSION) -t $(REPO):latest -f ./Dockerfile .
	docker push $(DOCKER_HUB):$(VERSION)
	docker push $(DOCKER_HUB):latest
	# docker rmi $(REPO):$(VERSION)
 
build-image-gitlab:
	docker pull $(REPO):latest || true
	docker build --cache-from $(REPO):latest --network host -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .
	docker push $(REPO):$(VERSION) 
	docker push $(REPO):latest
	docker rmi $(REPO):$(VERSION)

env-up:
	if command -v docker-compose &> /dev/null; then \
		docker-compose -f docker/docker-compose-basic.yaml up -d; \
	else \
		docker compose -f docker/docker-compose-basic.yaml up -d; \
	fi

env-down:
	if command -v docker-compose >/dev/null 2>&1; then \
 		docker-compose -f docker/docker-compose-basic.yaml down; \
	else \
 		docker compose -f docker/docker-compose-basic.yaml down; \
 	fi

up:
	docker-compose -f docker/docker-compose.yaml up -d

down:
	docker-compose -f docker/docker-compose.yaml down

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