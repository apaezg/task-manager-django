# simple-task-manager-django
Task management system where each task should have its own status, description, and users assigned to it.

## Premises:
Statuses:  new, in progress, completed, archived.
The system uses Django roles for differentiate admins from regular users. 
Only the administrator should be able to archive tasks.
Users assigned to tasks receive notifications about changes by email.
Users are able to comment on the tasks. 
Only administrators can delete comments.

## Install:

```bash
$ git clone git@github.com:apaezg/simple-task-manager-django.git
```
### Docker
See installation instructions at: [docker documentation](https://docs.docker.com/install/)
### Docker Compose
Install [docker compose](https://github.com/docker/compose), see installation
instructions at [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
### Dependencies & Database
```bash
$ make build
$ make reset-db
```

## Run:
```bash
$ make server
```
Go to http://127.0.0.1:8000

Access as admin user with:
- username: admin, password: adminpass01

Access as regular user with:
- username: user, password: userpass01
