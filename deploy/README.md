# What is here
This directory contains files related to the construction of docker images and their deployment.

**api.dockerfile**: a Dockerfile used for building the Desk2 backend application located at ./api.

**api.dockerignore**: files specified here will be ignored when building the container.

**docker-compose.yaml**: declares a local deployment of Desk2. Includes Redis and PostgreSQL images with persistent storage.

# Deploying
> All the commands here are supposed to be ran from the root of the repository

> You might need to add `sudo` before docker commands depending on your system configuration

## Prerequisites:
- Install [Docker](https://docs.docker.com/get-docker/)
- Make sure you have docker-compose installed (you can check by running `docker-compose --version` command)

## Building an image
> You may skip this step if you choose to use Tilt for local deployment

To build an image, simply following command.

`docker build --file deploy/api.dockerfile -t desk2-api .`

## Deploying with docker-compose
### Environment variable files
local-docker-compose.yml uses two files with environment variables: api.env and postgres.env. They should be placed in the ./deploy folder. After their creation your project's structure should look like this:

```
.
├── api
├── deploy
│  ├── api.dockerfile
│  ├── api.dockerignore
│  ├── api.env
│  ├── local-docker-compose.yaml
│  ├── postgres.env
│  └── README.md
├── README.md
└── Tiltfile
```

#### ./deploy/api.env
This file contains django secret and database configurations. Example content:

```
SECRET_KEY='i-am-your-father'

DATABASE_ENGINE='django.db.backends.postgresql'
DATABASE_NAME='university'
DATABASE_USER='postgres'
DATABASE_PASSWORD='postgres'
DATABASE_HOST='postgres'
DATABASE_PORT='5432'

REDIS_HOST=redis
```

#### ./deploy/postgres.env
This files contains PostgreSQL configurations. Make sure it uses the same values that api.env uses. Example content:

```
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='postgres'
POSTGRES_DB='university'
```

### Running with docker-compose
To launch the application, execute the following command

`docker-compose -f deploy/local-docker-compose.yaml up`

It starts three services with names desk2-api, postgres and redis. You'll be able to see joined logs of all the services in the terminal where you executed this command, as well as their deployment status. You can stop all the services at once by passing a CTRL+C interrupt in the terminal.

If you don't want your terminal to be blocked, add a `--detach` flag to it. If you do that, you'll need to use the following command to stop the service:

`docker-compose -f deploy/local-docker-compose.yaml down`

### Debugging
#### Inspecting logs
You can inspect the logs of each service with the following command:

`docker-compose -f deploy/local-docker-compose.yaml logs <service-name>`

To follow the logs, add `--follow` flag to the command.

#### Execing into containers
You can exec into a running container of one of the services with the following command:

`docker exec -it deploy_<service-name>_1 sh`

It opens an SSH session into the container. When done, use `exit` command to exit the container.


## Deploying with Tilt
### Prerequisites
- Install [Tilt](https://docs.tilt.dev/install.html).
  - Make sure to add it to $PATH.
  - You don't need to install Kubernetes utilities.
- Make sure that your docker-compose version is 1.29.2 or lower (docker-compose logs don't show up in Tilt when using docker-compose version 2.0.0 and higher).
  - You can download the appropriate version at the [official docker-compose release page](https://github.com/docker/compose/releases).
- (For linux) [setup Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/).

### Running Tilt
Execute the following command:

`tilt up`

That's it. Now you have a running local docker-compose deployment with live updates and quick rebuilds.

### Debugging
Press (space) in the terminal where you ran `tilt-up` or enter go to http://localhost:10350/ in your browser. There you'll be able to monitor the status of the services you deployed. Go to the appropriate service to view its logs.

### Cleanup
Don't forget to run `tilt down` to stop the deployment after you finish working with it. 
