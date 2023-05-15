VERSION := $(or ${CI_COMMIT_SHORT_SHA},latest)
REPO=searturky/punch-web

build-local: build
	docker build -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .

build-image:
	docker build -t $(REPO):$(VERSION) -t $(REPO):latest -f ./Dockerfile .
	docker push $(REPO):$(VERSION)
	docker push $(REPO):latest
	docker rmi $(REPO):$(VERSION)

check: install
	yarn lint

test: install
	yarn test:ci	

build: install
	yarn build

install:
	yarn

