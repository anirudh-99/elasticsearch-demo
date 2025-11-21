# Elasticsearch demo for hand's on

- For running frontend
  ```
  npm run serve
  ```
- For running backend:
  ```
  fastapi run
  ```
- For running elasticsearch container:
  ```
  docker run --name es01 \
        -p 9200:9200 \
        -e "discovery.type=single-node" \
        -e "xpack.security.enabled=false" \
        elasticsearch:9.2.0
  ```