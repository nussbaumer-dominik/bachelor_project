from neo4j import GraphDatabase, unit_of_work, __version__
import time
import sys

@unit_of_work(timeout=300)
def query_fun(tx, query):
    result = tx.run(query)
    return result.single()

def run_query(session, system_variant, sf, query_id, query_spec, results_file):
    start = time.time()
    print(f"Running query {query_id}...")
    # turn on the parallel runtime for the Enterprise edition
    if system_variant == "enterprise" and query_id != 9:
        query_spec = f"CYPHER runtime=parallel {query_spec}"
    result = session.read_transaction(query_fun, query_spec)
    end = time.time()
    duration = end - start
    results_file.write(f"Neo4j-{__version__}\t{system_variant}\t{sf}\t{query_id}\t{duration:.4f}\t{result[0]}\n")
    results_file.flush()
    print(f"Query {query_id} completed")
    return (duration, result)

if len(sys.argv) < 2:
    print("Usage: client.py sf <system variant>")
    print("Where sf is the scale factor and the system variant is the edition used (e.g. community, enterprise)")
    exit(1)

sf = sys.argv[1]

if len(sys.argv) > 2:
    system_variant = sys.argv[2]
else:
    system_variant = ""

driver = GraphDatabase.driver("bolt://localhost:7687")
session = driver.session()

with open(f"results/neo4j-results.csv", "a+") as results_file:
    for i in range(1, 10):
        print(f"Query {i}")
        with open(f"cypher/lsqb/q{i}.cypher", "r") as query_file:
            run_query(session, system_variant, sf, i, query_file.read(), results_file)

session.close()
driver.close()