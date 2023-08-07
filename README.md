
# Proxidize Backend Simulation

Proxidize Django backend aims to provide a robust API for managing simulated modems, with endpoints that allows the user to register, login, control IP rotations, toggle critical mode to mask sensitive data and more. Additionally, the project includes the implementation of Celery and Celery Beat to offload background tasks and perform simulated periodic IP rotations. The sqlite database will be pre-populated with dummy Modems and SMS instances.

Pytest is used for unit testing.

## Installation

Clone the repository locally & cd into the directory

```
git clone https://github.com/YazidKurdi/proxidize-API.git && cd proxidize-API
```

#### Running the backend server (Docker)

1. Pull the docker images and spin up the containers:
```
docker-compose up
```

2. Visit  http://127.0.0.1:8000
## Endpoints

### Login & Signup
- Register a new user (POST): http://127.0.0.1:8000/dj-rest-auth/registration/
- Login (POST): http://127.0.0.1:8000/dj-rest-auth/login/

### Modem
- List modems (GET): http://127.0.0.1:8000/api/list_modems/ - Paginated
- Toggle critical mode to mask sensitive data (PUT): http://127.0.0.1:8000/api/crit_mode/
- Shuffle modems (GET): http://127.0.0.1:8000/api/rotate/
- Reboot a single modem granting new IPs (GET): http://127.0.0.1:8000/api/reboot_modem/
- Periodic IP rotation for modem(s) (GET): http://127.0.0.1:8000/api/custom_rot/
- Clear all periodic tasks (GET): http://127.0.0.1:8000/api/clear_rot/

### SMS

- List SMS messages by modem index (GET): http://127.0.0.1:8000/api/sms/get/
- List SMS messages by phone number (GET) http://127.0.0.1:8000/api/sms/fetch_sms_phone_number/

#

Endpoints, query parameters, responses are similiar to proxidize's API documentation


## Unit Testing

Run ```docker-compose exec web pytest``` while in the main project directory
