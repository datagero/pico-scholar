
## Docker

### Set-up MySQL Container
`export MYSQL_ROOT_PASSWORD=my-secret-pw`


`docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -d mysql:latest`

`docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=my-secret-pw -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -d mysql:latest`

`docker exec -it mysql-container mysql -uroot -p`

#### Run with persistent local storage
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest

### Set-up backend APP container
From the `\backend` directory,


### Note - Stage1 for python environment docker image
If you need to create the python enviornment, you have to run and host Dockerfile.stage1
Below is an example for building the image and push it to the docker hub under my username (datagero).
Then the Dockerfile (stage 2 - build the backend for the App) will pull this image from the dockerhub.

First, if the python environment changed generate requirements.txt using poetry on your local machine:

`poetry export -f requirements.txt > requirements.txt`

Then, build the image to set-up our python environment

```
docker build -t pico-env-builder --target pico-env-builder -f Dockerfile.stage1 .
docker tag pico-env-builder datagero/pico-env-builder:latest 
docker push datagero/pico-env-builder:latest
```

Build the Docker Image:

`docker build -t pico-backend .`

Run the Docker Container:

`docker run --env-file .env -d -p 8000:8000 pico-backend`

Go inside the container

`docker exec -it d10bacbf42af /bin/bash`


### Create a Docker Network
```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker network create mynetwork

docker run -it --network mynetwork --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest

docker run -it --network mynetwork --env-file .env -p 8000:8000 pico-backend
```
