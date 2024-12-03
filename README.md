# WRCT Reviews

A website to host albums/reviews

## Getting started with local development
1. Create a python virtual environment
    ```
    python -m venv venv
    ```
1. Activate the new virtual environment
    ```
    source venv/bin/activate
    ```
1. Install required python modules
    ```
    pip install -r requirements.txt
    ```
1. Add this line to docker-compose.yml under `reviews-backend:` right above `networks:`
    ```
        ports:
          - "8001:8001"
    ```
1. Build docker container from Dockerfile
    ```
    docker build .
    ```
1. Launch docker container. If you want it to live in the background instead of sitting in your terminal, add `-d` to the end.
    ```
    docker compose up
    ```
1. Open a shell inside the docker container
    ```
    docker exec -it wrct-reviews-backend bash
    ```
1. Create an admin user account for yourself for local development
    ```
    python3 manage.py createsuperuser
    ```
1. In your browser, go to [127.0.0.1:8001](http://127.0.0.1:8001/) or [0.0.0.0:8001](http://0.0.0.1:8001/) to access the app. You can also access the Django admin page by appending [/admin](http://127.0.0.1:8001/admin) to the URL.

1. Add some albums if you need test data. *TODO:* Add some test data to this repo or add an easy way to copy data from the real database to local developemnt.

## Credits

CASSIDY
