# PDF Label UI Set Up

PDF Label UI is intended to be a user interface for easily labelling pdfs for training a ML model.

To set up this project, sign into github from the CLI, and enter
```shell
setup.sh ( not supported yet - do not use)
```
and the project will initialize:\
* the backend, frontend, and altoAPI will get pulled from github
* if docker and docker-compose is not installed, they will be installed
* the docker containers for the frontend, backend and altoAPI will be launched



Currently, it is best to run this application using docker compose. Docker must be running to launch this command.
(docker-compose up -d --build)