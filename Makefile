DOCKERPATH = docker

DOCKER_COMPOSE = docker/docker-compose.yml

.PHONY: build
build:
	docker-compose -f $(DOCKER_COMPOSE) build

.PHONY: up
up:
	docker-compose -f $(DOCKER_COMPOSE) up

.PHONY: down
down:
	docker-compose -f $(DOCKER_COMPOSE) down

.PHONY: connect_gobgp_1
connect_gobgp_1:
	docker exec -it docker_gobgp_1_1 /bin/bash

.PHONY: connect_gobgp_2
connect_gobgp_2:
	docker exec -it docker_gobgp_2_1 /bin/bash

.PHONY: connect_control
connect_control:
	docker exec -it docker_gobgp_control_1 /bin/bash
