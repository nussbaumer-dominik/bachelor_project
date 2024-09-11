import argparse
import os

from dotenv import load_dotenv, find_dotenv

from neo4j_connection import Neo4jConnection
from postgres_connection import PostgreSQLConnection

load_dotenv(find_dotenv(), override=True)

# Database configurations
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# Query directories
NEO4J_QUERY_DIR = os.getenv('NEO4J_QUERY_DIR')
POSTGRES_QUERY_DIR = os.getenv('POSTGRES_QUERY_DIR')

parser = argparse.ArgumentParser(
    description="Benchmark Neo4j and PostgreSQL with the given queries",
    prog="BachelorsThesisBenchmark",
    epilog="Please make sure to set the environment variables before running the script"
)

parser.add_argument("-t", "--timeout", type=int, default=120, help="Timeout in seconds for each individual query run")
parser.add_argument("-r", "--runs", type=int, default=5, help="Number of runs for each query")
parser.add_argument("-n", "--neo4j", action="store_true", help="Run Neo4j queries")
parser.add_argument("-p", "--postgres", action="store_true", help="Run PostgreSQL queries")
parser.add_argument("-nd", "--neo4j-dir", type=str, default="neo4j_results",
                    help="Result directory containing Neo4j queries")
parser.add_argument("-pd", "--postgres-dir", type=str, default="postgres_results",
                    help="Result directory containing PostgreSQL queries")


def read_queries(directory, extension):
    queries = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(extension):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                query = file.read().strip()
                queries.append((os.path.splitext(filename)[0], query))

    return queries


def main():
    args = parser.parse_args()
    print(args)
    neo4j_queries = read_queries(NEO4J_QUERY_DIR, '.cypher')
    postgres_queries = read_queries(POSTGRES_QUERY_DIR, '.sql')

    if len(neo4j_queries) > 0 and args.neo4j:
        neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        try:
            print("Running Neo4j Queries")
            neo4j_results, neo4j_query_stats = neo4j_conn.run_queries(
                neo4j_queries, result_dir=args.neo4j_dir,
                runs=args.runs, timeout_seconds=args.timeout
            )
            print("Neo4j Results", neo4j_results)
        finally:
            neo4j_conn.close()
    else:
        print("No Neo4j Queries to run")

    if len(postgres_queries) > 0 and args.postgres:
        postgres_conn = PostgreSQLConnection(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD)
        try:
            print("Running Postgres Queries")
            postgres_results, postgres_query_stats = postgres_conn.run_queries(
                postgres_queries,
                result_dir=args.postgres_dir,
                runs=args.runs,
                timeout_seconds=args.timeout
            )
            print("Postgres Results", postgres_results)
        finally:
            postgres_conn.close()
    else:
        print("No Postgres Queries to run")


if __name__ == "__main__":
    main()
