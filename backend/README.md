
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

If the python environment changed generate requirements.txt using poetry on your local machine:

`poetry export -f requirements.txt > requirements.txt`

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
