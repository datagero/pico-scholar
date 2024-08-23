
## Docker - Option 1: Run Locally

### Set-up MySQL Container with persistent local storage
```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v $(pwd)/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
```

Run the below to connect to the server from the terminal

```
docker exec -it mysql-container mysql -uroot -p
```


You can then run the backend locally by starting the server
```
fastapi dev backend/serverfastapi/main.py
```


## Docker - Option 2: Containerised application

If you wish to run the backend from a container, perform the below

From the `\backend` directory,

### Development Set-up
### Note - Stage1 for python environment docker image
If you need to create the python enviornment, you have to run and host Dockerfile.stage1
Below is an example for building the image and push it to the docker hub under my username (datagero).
Then the Dockerfile (stage 2 - build the backend for the App) will pull this image from the dockerhub.

First, if the python environment changed generate requirements.txt using poetry on your local machine. You may need to clean this output (e.g. remove system dependencies):

```
poetry export --with backend -f requirements.txt --output requirements.txt --without-hashes
```

Then, build the image to set-up our python environment. Since we're targeting the gitpod environment, then its best to build and push this to the registry from the gitpod env to avoid compatability issues.

```
docker build --no-cache -t pico-env-builder --target pico-env-builder -f Dockerfile.stage1 .
docker tag pico-env-builder datagero/pico-env-builder:latest 
docker push datagero/pico-env-builder:latest
```

Build the Docker Image:

```
docker build --no-cache  -t pico-backend .
```

## Docker - Run Full Containerised application
Create a Docker Network for both services to communicate

From the `\backend` directory,

First, make sure that we've built the pico-backend docker with the latest backend changes.
No need to run this if backend has not changed since last build.

`docker build -t pico-backend .`

Then, start a network with both the mysql-container and the pico-backend

```
docker network create mynetwork

export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run -it --network mynetwork --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v $(pwd)/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
docker run -it --network mynetwork --env-file .env_docker --name pico-backend -p 8000:8000 -p 8501:8501 pico-backend
```