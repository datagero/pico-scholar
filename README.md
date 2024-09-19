# PICO Scholar Project Overview 🚀

Welcome to **PICO Scholar**, an innovative platform created for researchers to manage, extract, and categorize critical PICO elements (Population, Intervention, Comparison, Outcome) from scientific documents. This project is part of the [TiDB Future App Hackathon 2024](https://devpost.com/software/pico-scholar) and aims to streamline the research process by enabling fast, efficient, and accurate document search and PICO extraction through advanced AI models.

## Important Note on Setup

To use the code in its current version, you **must set up a TiDB cluster** and configure the respective environment variables in the `.env` or Gitpod files. Additionally, you'll need to run the code locally to ingest data into TiDB. 

- Example CSV files with abstracts are available in the `backend/datalake` folder to help you get started.
- Please refer to the [Backend README](./backend/README.md) for more detailed information about the ingestion pipelines and the general process.

## Gitpod Setup

Gitpod was initially made available for the judges of the hackathon. In its current form, it will spin up a UI, but since it doesn't have pointers to data or API keys, the app will not be functional out of the box. However, the Gitpod setup can still be useful if you wish to **fork the repository** and add your own credentials and data privately.

## Try it!

You can explore the project through Gitpod by clicking the button below:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/new/#https://github.com/datagero/pico-scholar)

Set the following environment variables for full functionality:
```sh
TIDB_PASSWORD=<your-tidb-password>
OPENAI_API_KEY=<your-openai-api-key>
```

## For Local Development

1. **Set up environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```sh
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
   ```

2. **Run Docker Compose**:
   To spin up the containerized app, run:
   ```sh
   docker-compose up
   ```

3. Alternatively, spin up the individual components

### Front-end Setup
Navigate to `frontend/lamatidb` and run the following commands:
```
npm install
npm start
```
Access the frontend at `localhost:3000`.

### Back-end Setup

First, start the MySQL container:
```
export MYSQL_ROOT_PASSWORD=my-secret-pw
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v $(pwd)/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
```

Then, start the FastAPI server:
```
fastapi dev backend/serverfastapi/main.py
```

### Connect to MySQL Database

You can connect to the MySQL database with:
```
mysql -h 127.0.0.1 -P 3306 -u root -p
```

## Project Structure

- **Backend**: The API and data processing logic (see `/backend/README.md` for more details).
- **Frontend**: React-based interface for managing research queries and document reviews.

# Contributors
By: Matias V, Cristina DeLisle, Ben K, Will Gleason
