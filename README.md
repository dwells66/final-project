# Final Project

![Build Status](https://github.com/dwells66/final-project/actions/workflows/build.yml/badge.svg?branch=main)



Below are instructions for how to utilize the services contained in the repository. Fork this repo, and clone it onto your server. From inside you can run the commands below to build the docker containers. The database is created in the twitter_postgres_indexes repo. The SQL files included can be run to add the necessary cleaned up tables starting with clean_tables.sql, clean.sql, credentials.sql, and then spell.sql.

```
$ docker compose down -v
$ docker compose up -d --build
```
You should establish another connection to your server using the localhost:8080 address as well as port 1202 for your server's IP address. You can then access the website <http://localhost:8080> to view the app. 
