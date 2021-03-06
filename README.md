# wiki-search

A simple web service to search Wikipedia.

[![Maintainability](https://api.codeclimate.com/v1/badges/29c44f43d1b6afba3846/maintainability)](https://codeclimate.com/github/teners/wiki-search/maintainability)
[![Actions Status](https://github.com/teners/wiki-search/workflows/wiki-search/badge.svg)](https://github.com/teners/wiki-search/actions?workflow=wiki-search)

![](https://media.giphy.com/media/3o6Zt9EEeSSNLd2nqU/giphy.gif)

## Using without Docker

### Installation

Poetry[\[1\]][1] is used for dependencies management in wiki-search.
In case you don't have it, install it first.  

Install dependencies:

```shell script
poetry install
```

### Running the application

Make sure you have Redis server up and running, export it's
address and port as URI to `REDIS_URI` environmental variable
or put it into `.env` file in the project root.

Then, simply run

```shell script
poetry run uvicorn wiki_search.main:app
```

Now you can go to http://localhost:8000/redoc to browse the
OpenAPI specification.

_Note_: for local development you can use uvicorn's `--reload`
option so that uvicorn monitor and reload the application when
the code should change.


## With Docker

In case you don't have Redis server running separately,
you might want to use docker-compose since this repo contains
`docker-compose.yml` that includes Redis service as well.

From the project root run

```shell script
docker-compose up
``` 

This command would build wiki-search image and run it for you
in tow with Redis.

Alternatively, if you have Redis running somewhere else, you
can build wiki-search image manually with `docker build`[\[2\]][2]
command and run with `docker run`[\[3\]][3] providing `REDIS_URI`
through `--env-file` or `--env`.

## References

\[1\] [Poetry][1]

\[2\] [`docker build` reference][2]

\[3\] [`docker run` reference][3]


[1]: http://poetry.eustace.io "Poetry" 
[2]: https://docs.docker.com/engine/reference/commandline/build/ "docker build reference"
[3]: https://docs.docker.com/engine/reference/commandline/run/ "docker run reference"
