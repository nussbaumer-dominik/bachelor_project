# Comparative Analysis of Graph Data Modeling and Querying in Neo4j and PostgreSQL

This repository contains the code and scripts for the comparative analysis of graph data modeling and querying in Neo4j
and PostgreSQL. The analysis used the LDBC SNB and LSQB benchmarks as a foundation.

## Getting started

### Install dependencies

1. Install Docker on your machine.

1. Install the required dependencies:

   ```bash
   scripts/install-dependencies.sh
   ```

1. Navigate to the benchmark directory and install the python dependencies:

    ```bash
    cd benchmark
    pip install -r requirements.txt
    ```

1. (Optional) "Warm up" the system using `scripts/benchmark.sh`, e.g. run all systems through the smallest `example`
   data set. This should fill Docker caches.

### Creating the input data

Data sets should be provided in two formats:

* `data/social-network-sf${SF}-projected-fk`: projected foreign keys, the preferred format for most graph database
  management systems.
* `data/social-network-sf${SF}-merged-fk`: merged foreign keys, the preferred format for most relational database
  management systems.

An example data set is provided with the substitution `SF=example`:

* `data/social-network-sfexample-projected-fk`
* `data/social-network-sfexample-merged-fk`

Pre-generated data sets are available in
the [SURF/CWI data repository](https://repository.surfsara.nl/datasets/cwi/lsqb).

To download the data sets, set the `MAX_SF` environment variable to the size of the maximum scale factor you want to
use (at least `1`) and run the download script.

For example:

```bash
export MAX_SF=1
scripts/download-projected-fk-data-sets.sh
scripts/download-merged-fk-data-sets.sh
```

For more information, see
the [download instructions and links](https://github.com/ldbc/data-sets-surf-repository/#labelled-subgraph-query-benchmark-lsqb).

#### Running out benchmarking suite

The benchmark run consists of two key steps: loading the data and running the queries on the database.

Some systems need to be online before loading, while others need to be offline. To handle these differences in a unified
way, we use three scripts for loading:

* `pre-load.sh`: steps before loading the data (e.g. starting the DB for systems with online loaders)
* `load.sh`: loads the data
* `post-load.sh`: steps after loading the data (e.g. starting the DB for systems with offline loaders)

The `init-and-load.sh` script calls these three scripts (`pre-load.sh`, `load.sh`, and `post-load.sh`).
Therefore, to run the benchmark and clean up after execution, use the following three scripts:

* `init-and-load.sh`: initialize the database and load the data
* `python benchmark/benchmark.py -t 300 -r 5 -np`: run the benchmark with a timeout of 300 seconds and 5 repetitions for
  both Neo4j and Postgres. It will execute all queries that are directly located in the cypher and sql directories.

Example usage that loads scale factor 0.3 to Neo4j:

```bash
cd neo
export SF=0.3
./init-and-load.sh
cd ../benchmark
python benchmark.py -t 300 -r 5 -n
```

Benchmark Suite usage:
```bash
usage: BachelorsThesisBenchmark [-h] [-t TIMEOUT] [-r RUNS] [-n] [-p] [-nd NEO4J_DIR] [-pd POSTGRES_DIR]

Benchmark Neo4j and PostgreSQL with the given queries

options:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds for each individual query run
  -r RUNS, --runs RUNS  Number of runs for each query
  -n, --neo4j           Run Neo4j queries
  -p, --postgres        Run PostgreSQL queries
  -nd NEO4J_DIR, --neo4j-dir NEO4J_DIR
                        Result directory containing Neo4j queries
  -pd POSTGRES_DIR, --postgres-dir POSTGRES_DIR
                        Result directory containing PostgreSQL queries

Please make sure to set the environment variables before running the script
```

The graphs can be generated using the `evalute.py` script in the benchmark directory. Edit main method to change what graphs are generated.

#### Running the benchmark how the LSQB team envisioned it

Follow the steps described in the section above but instead of running the python benchmark suite you will have to use the `run.sh` in the corresponding system directories.
Example usage that loads scale factor 0.3 to Neo4j:

```bash
cd neo
export SF=0.3
./init-and-load.sh && ./run.sh && ./stop.sh
```

## Labelled Subgraph Query Benchmark (LSQB)

:page_facing_up: [LSQB: A Large-Scale Subgraph Query Benchmark](https://dl.acm.org/doi/pdf/10.1145/3461837.3464516),
GRADES-NDA'21
paper ([presentation](https://docs.google.com/presentation/d/13B5XwwSlgi-r3a9tKNxo8HmdIRzegO6FMB-M6I1RW0I))

### Overview

A benchmark for subgraph matching but with type information (vertex and edge types). The primary goal of this benchmark
is to test the query optimizer (join ordering, choosing between binary and n-ary joins) and the execution engine (join
performance, support for worst-case optimal joins) of graph databases. Features found in more mature database systems
and query languages such as date/string operations, query composition, complex aggregates/filters are out of scope for
this benchmark.

The benchmark consists of the following 9 queries:

![](patterns.png)

## Friends-of-Friends

## Shortest Path