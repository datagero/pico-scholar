
## Docker - Option 1: Run Locally

### Set-up MySQL Container with persistent local storage
```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
```

Run the below to connect to the server from the terminal
`docker exec -it mysql-container mysql -uroot -p`


### Optional - Set-up backend APP container
If you wish to run the backend from a container, perform the below

From the `\backend` directory,

### Note - Stage1 for python environment docker image
If you need to create the python enviornment, you have to run and host Dockerfile.stage1
Below is an example for building the image and push it to the docker hub under my username (datagero).
Then the Dockerfile (stage 2 - build the backend for the App) will pull this image from the dockerhub.

First, if the python environment changed generate requirements.txt using poetry on your local machine:

`poetry export -f requirements.txt > requirements.txt`

Then, build the image to set-up our python environment. Since we're targeting the gitpod environment, then its best to build and push this to the registry from the gitpod env to avoid compatability issues.

```
docker build -t pico-env-builder --target pico-env-builder -f Dockerfile.stage1 .
docker tag pico-env-builder datagero/pico-env-builder:latest 
docker push datagero/pico-env-builder:latest
```

Build the Docker Image:

`docker build -t pico-backend .`

Run the Docker Container:

`docker run --env-file .env_docker -d -p 8000:8000 pico-backend`

Go inside the container

`docker exec -it d10bacbf42af /bin/bash`

## Docker - Option 2: Containerised application
Create a Docker Network for both services to communicate

From the `\backend` directory,


```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker network create mynetwork

docker run -it --network mynetwork --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest


docker build -t pico-backend .
docker run -it --network mynetwork --env-file .env_docker -p 8000:8000 pico-backend
```
