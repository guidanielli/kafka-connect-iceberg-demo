DC=docker-compose 
ICEBERG_IMAGE_NAME=iceberg-build:latest
ZIP_FILE_NAME=iceberg-kafka-connect-runtime-hive-1.10.1-SNAPSHOT.zip
ZIP_DEST=./kafka-connect-plugins/distributions/

build: 
	$(DC) build

up: 
	$(DC) up -d

down: 
	$(DC) down

logs: 
	$(DC) logs -f

exec: 
	$(DC) exec $(service) $(cmd)

clean: 
	docker system prune -f

rebuild: 
	down build up

down-clean: 
	$(DC) down -v

start-producer: 
	$(DC) up -d producer

iceberg-build:
	docker build -t $(ICEBERG_IMAGE_NAME) -f ./iceberg-sink-plugin/Dockerfile .
iceberg-copy: iceberg-build
	@echo "Creating temporary container..."
	docker create --name iceberg-temp $(ICEBERG_IMAGE_NAME)
	@echo "Copying zip file to host..."
	mkdir -p $(ZIP_DEST)
	docker cp iceberg-temp:/path/in/container/$(ZIP_FILE_NAME) $(ZIP_DEST)
	@echo "Removing temporary container..."
	docker rm iceberg-temp


.PHONY: start-producer iceberg-build iceberg-copy
