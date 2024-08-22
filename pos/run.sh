#!/bin/bash

set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

. pos/vars.sh
. scripts/import-vars.sh

#python3 pos/client.py ${SF} PostgreSQL $@
python3 pos/client-new.py ${SF} PostgreSQL $@
