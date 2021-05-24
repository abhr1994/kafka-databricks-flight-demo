# kafka-databricks-flight-demo
This repo consists of code to ingest data from Flights API into kafka and analyse in databricks

## Flow Diagram

![Alt text](design.png?raw=true "Flow Diagram")

```markdown

In this project,

1. We used opensky-network restapis to ingest realtime flight data into Kafka. We used kafka-python module to write the api data to Kafka topic.
2. We used Infoworks Ingestion tool to stream data from Kafka topic to raw zone in Delta Lake
3. We then transform the streamed data by doing necesssary joins and aggregations in Databricks notebook and write the data to a final table for consumption.
4. We then write the tranformed data to Bigquery and visualise using Google Datastudio.

```

## Steps to install Kafka inside Docker

Add below contents inside your docker-compose.yml file and then run sudo docker-compose up -d

```markdown
version: '2'
networks:
  kafka-net:
    driver: bridge

services:
  zookeeper-server:
    image: 'bitnami/zookeeper:latest'
    networks:
      - kafka-net
    ports:
      - '2181:2181'
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
  kafka-server:
    image: 'bitnami/kafka:latest'
    networks:
      - kafka-net    
    ports:
      - '9092:9092'
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://hostname:9092
      - ALLOW_PLAINTEXT_LISTENER=yes
    depends_on:
      - zookeeper-server
```

## Infoworks Ingestion from Kafka to Raw zone

![Alt text](infoworks.png?raw=true "Ingestion")

## Kafka Messages

![Alt text](kafka_records.png?raw=true "Kafka Messages")

## Nearest Airports Output (Visualised using DataStudio)

![Alt text](datastudio.png?raw=true "Nearest Airports")
