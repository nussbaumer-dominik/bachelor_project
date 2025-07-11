#!/bin/bash

# script to run benchmarks on the systems passed as its argument

set -eu
set -o pipefail

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

SFS="0.3"
SYSTEMS="neo"
WARMUP_SF="example"
RUNS=5

export SF
for SF in ${SFS}; do
    echo Running benchmark on scale factor ${SF}
    for SYSTEM in ${SYSTEMS}; do
        echo Benchmarking system ${SYSTEM}
        cd ${SYSTEM}
        for RUN in $(seq 1 ${RUNS}); do
            echo "Run ${RUN} of ${RUNS}"
            ./init-and-load.sh && ./run.sh && ./stop.sh
        done
        cd ..
    done
done
