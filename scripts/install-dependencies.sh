#!/bin/bash

set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

echo Installing Pip package

pip3 config --user set global.progress_bar off
# clients
pip3 install --user neo4j==5.23.1
pip3 install --user wheel
pip3 install --user psycopg2-binary
pip3 install --user psycopg

# visualization
pip3 install --user matplotlib pandas seaborn natsort
