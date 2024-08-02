#!/bin/bash

set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

. pos/vars.sh

cat sql/general/drop.sql | docker exec -i ${POSTGRES_CONTAINER_NAME} psql -U postgres

echo Loading data to Postgres...
cat sql/general/schema.sql | docker exec -i ${POSTGRES_CONTAINER_NAME} psql -U postgres
sed "s|PATHVAR|/data|" sql/general/snb-load.sql | docker exec -i ${POSTGRES_CONTAINER_NAME} psql -U postgres
echo Done

echo Initializing views and indexes...
cat sql/general/views.sql | docker exec -i ${POSTGRES_CONTAINER_NAME} psql -U postgres
echo Done
