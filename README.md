This project is built as part of the [TiDB Future App Hackathon 2024](https://tidbhackathon2024.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open)

Please read through the project inspiration and objectives, as well as a DEMO:
https://devpost.com/software/pico-scholar

This project will be made public and its technical components fully documented at that time.

We recommend you try the app through Gitpod (below) which provides all you need to get started.

## Try it!

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/new/#https://github.com/datagero/pico-scholar)

You will have to set your TIDB_PASSWORD for our cluster, and (optionally) OPENAI_API_KEY for access to all features...

## For your local development / use:

1. Get your OpenAI key: https://platform.openai.com/docs/quickstart
2. You need to set-up the below environment variables on a .env file at project level (and .env_docker at the backend folder)

```
OPENAI_API_KEY=

TIDB_HOST=
TIDB_USERNAME=
TIDB_PASSWORD=
TIDB_PORT=
TIDB_DB_NAME=

MYSQL_HOST=127.0.0.1
MYSQL_USERNAME=root
MYSQL_PASSWORD=my-secret-pw
MYSQL_PORT=3306
MYSQL_DB_NAME=docker_test
PYTHONPATH=./backend

FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

## Docker Compose to run the containerised app
```
docker-compose up
```

## Front-end local run
go to `frontend/lamatidb`

```
npm install
npm start
```
You can access the frontend through localhost:3000

## Back-end FastAPI local run
First, set-up MySQL container with persistent local storage

```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v $(pwd)/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
```

Then start the server
```
fastapi dev backend/serverfastapi/main.py
```

You can access the database through the terminal
```
mysql -h 127.0.0.1 -P 3306 -u root -p
```
