# DDFF's registreringsdatabase

Bygget på Djangoframeworket.

## Setup
- Check projektet ud af git
- Optionelt: 
  - Lav et virtual environment til python: `python3 -m venv .venv`
  - Aktiver environment: `source .venv/bin/activate`
- Installer requirements: `pip install -r requirements.txt`
- Kopier static files over i "static" folderen: `python manage.py collectstatic`

- For at starte serveren, brug det medfølgende script:
  - `./regbase-server.sh start`

## Konfiguration

### Følgende environment-variable _skal_ sættes:

- DB_MSMYSQL_USER
- DB_MSMYSQL_PASSWORD
- DB_MSMYSQL_NAME
- DB_MSMYSQL_HOST
- DB_MSMYSQL_PORT

### Følgende environment-variable _bør_ sættes
- DJANGO_SECRET_KEY
- DB_CONN_MAX_AGE
- DJANGO_ALLOWED_HOSTS

### Følgende environment-variable _kan_ sættes.

- DJANGO_DEBUG

### Andet

`./pictures` er sat som folder til billeder.
`./static` er sat til static files.

