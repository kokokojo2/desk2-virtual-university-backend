FROM hylang:python3.10-alpine3.14

RUN mkdir /app
WORKDIR /app

# copy the app
COPY api/ ./

# install dependencies
RUN apk update && \
    apk upgrade && \
    # postgresql for psycopg2==2.9.1. This solution takes less space than "apk add postgresql-dev". Taken from https://stackoverflow.com/questions/46711990/error-pg-config-executable-not-found-when-installing-psycopg2-on-alpine-in-dock
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    # actual pip installation
    pip install -r requirements.txt --no-cache-dir && \
    # cleanup
    apk --purge del .build-deps

# give the init script run permissions
RUN ["chmod", "+x", "migrate-and-run.sh"]

ENTRYPOINT ["/bin/sh", "-c", "source migrate-and-run.sh"]