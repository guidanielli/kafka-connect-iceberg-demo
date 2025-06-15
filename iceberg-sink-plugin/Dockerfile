FROM openjdk:17-jdk-slim AS build

ENV ICEBERG_KAFKA_CONNECT_PATH="/app/iceberg/kafka-connect/kafka-connect-runtime/build/distributions/"
ENV ICEBERG_KAFKA_CONNECT_PLUGIN_PATH='/app/kafka-connect-plugins/'
ENV ICEBERG_KAFKA_CONNECT_VERSION_PACKAGE="iceberg-kafka-connect-runtime-hive-1.10.1-SNAPSHOT.zip"
ENV ICEBERG_BUILD_TAG="1.9.1"

WORKDIR /app

RUN apt-get update \
    && apt-get \
    install -y  \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && git clone --branch "apache-iceberg-${ICEBERG_BUILD_TAG}" https://github.com/apache/iceberg.git

WORKDIR /app/iceberg

RUN curl -sLo gradle-wrapper.zip https://services.gradle.org/distributions/gradle-7.6-bin.zip  \
    && unzip gradle-wrapper.zip \
    && rm gradle-wrapper.zip \
    && ./gradlew -x test -x integrationTest clean build \
    && mkdir -p "${ICEBERG_KAFKA_CONNECT_PLUGIN_PATH}" \
    && unzip -q "${ICEBERG_KAFKA_CONNECT_PATH}/${ICEBERG_KAFKA_CONNECT_VERSION_PACKAGE} -d ${ICEBERG_KAFKA_CONNECT_PLUGIN_PATH}" \ 
    && rm -rf /app/iceberg/*


FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy the built artifacts from the build stage
COPY --from=build ${ICEBERG_KAFKA_CONNECT_PLUGIN_PATH} ${ICEBERG_KAFKA_CONNECT_PLUGIN_PATH}

# Default command
CMD ["bash"]    