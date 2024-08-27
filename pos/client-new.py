import psycopg
import time
import sys

from contextlib import contextmanager

@contextmanager
def timeout(cursor, t):
    cursor.execute(f"SET statement_timeout TO {int(t * 1000)}")
    try:
        yield
    finally:
        cursor.execute("SET statement_timeout TO 0")

def run_query(con, variant, sf, query_id, query_spec, system, results_file):
    print(f"Running query {query_id}...")
    start = time.time()
    with con.cursor() as cur:
        try:
            with timeout(cur, 300):  # 300 seconds timeout
                cur.execute(query_spec)
            result = cur.fetchall()
        except psycopg.OperationalError as e:
            if "timeout" in str(e).lower():
                print(f"Query {query_id} timed out")
                return
            raise
    end = time.time()
    duration = end - start
    results_file.write(f"{system}-new\t{variant}\t{sf}\t{query_id}\t{duration:.4f}\t{result[0][0]}\n")
    results_file.flush()
    print(f"Completed {query_id} in {duration:.4f} seconds")
    return (duration, result)

if len(sys.argv) < 2:
    print("Usage: client.py sf [system] [variant]")
    print("where sf is the scale factor and system/variant are optional (default: system='PostgreSQL', variant='')")
    sys.exit(1)
else:
    sf = sys.argv[1]

system = sys.argv[2] if len(sys.argv) > 2 else "PostgreSQL"
variant = sys.argv[3] if len(sys.argv) > 3 else ""

con = psycopg.connect("host=localhost user=postgres password=mysecretpassword port=5432")

with open(f"results/postgres-results.csv", "a+") as results_file:
    for i in range(1, 10):
        with open(f"sql/q{i}.sql", "r") as query_file:
            run_query(con, variant, sf, i, query_file.read(), system, results_file)
