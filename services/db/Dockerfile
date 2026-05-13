FROM postgres:17

RUN apt-get update && apt-get install -y \
    postgresql-server-dev-17 \
    git build-essential

RUN git clone https://github.com/postgrespro/rum.git \
 && cd rum \
 && make USE_PGXS=1 \
 && make USE_PGXS=1 install
