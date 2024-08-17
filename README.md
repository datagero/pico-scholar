
1. For the demo scripts, get your OpenAI key: https://platform.openai.com/docs/quickstart
2. You need to set-up the below environment variables on a .env file at project level

```
OPENAI_API_KEY=
TIDB_HOST=
TIDB_USER=
TIDB_USERNAME=
TIDB_PASSWORD=
TIDB_PORT=
TIDB_DB_NAME=
```


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
fastapi dev serverfastapi/main.py


## Docker
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run --name pico-mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -d mysql:latest
docker run --name pico-mysql-container -e MYSQL_ROOT_PASSWORD=my-secret-pw -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -d mysql:latest
docker exec -it pico-mysql-container mysql -uroot -p


docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=thisissecurepassword -v /Users/datagero/Documents/offline_repos/lamatidb/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest


mysql -h 127.0.0.1 -P 3306 -u root -p