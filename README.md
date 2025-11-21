# Elasticsearch demo for hand's on

- For running frontend
  ```
  npm run serve
  ```
- For running backend:
  - Run elastic search:
    ```
    docker run --name es01 \
          -p 9200:9200 \
          -e "discovery.type=single-node" \
          -e "xpack.security.enabled=false" \
          elasticsearch:9.2.0
    ```
  - Index the data by running:
    ```
    python ./backend/index_data.py
    ```
  - Run backend server
    ```
    fastapi run
    ```
