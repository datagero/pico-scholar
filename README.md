
1. For the demo scripts, get your OpenAI key: https://platform.openai.com/docs/quickstart
2. You need to set-up the below environment variables on a .env file at project level

```
DEVELOPER_NAME=

TIDB_HOST=
TIDB_USER=
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

## Try it!

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/new/#https://github.com/datagero/pico-scholar)

You will have to manually paste a .env inside the backend/ folder to run the App.

## Swagger (to be replaced by FastAPI)
To run the swagger/flask server (replace [PROJECT_ROOT_PATH])

```
export PROJECTROOTPATH=/Users/datagero/Documents/offline_repos
export PYTHONPATH=$PYTHONPATH:/$PROJECTROOTPATH/lamatidb/server
python -m swagger_server
```

Once the server is running, you can visit `http://localhost:8080//ui/` to review documentation and test the API.

For now, the server runs on test by default (with hardcoded outputs). You can modify this in `server/swagger_server/__main__.py`

## FastAPI
First, set-up MySQL container with persistent local storage

```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
```

Then start the server
`fastapi dev backend/serverfastapi/main.py`

You can access the database through the terminal
`mysql -h 127.0.0.1 -P 3306 -u root -p`