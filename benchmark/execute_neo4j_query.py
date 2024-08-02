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
    neo4j_queries = read_queries(NEO4J_QUERY_DIR, '.cypher')
    postgres_queries = read_queries(POSTGRES_QUERY_DIR, '.sql')

    neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        print("Running Neo4j Queries")
        if len(neo4j_queries) > 0:
            neo4j_results, neo4j_query_stats = neo4j_conn.run_queries(neo4j_queries)
            print("Neo4j Results", neo4j_results)
            Neo4jConnection.save_all_query_stats(neo4j_query_stats, "neo4j_results")
        else:
            print("No Neo4j Queries to run")

    finally:
        neo4j_conn.close()

    postgres_conn = PostgreSQLConnection(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD)
    try:
        print("Running Postgres Queries")
        postgres_results, postgres_query_stats = postgres_conn.run_queries(postgres_queries)
        print("Postgres Results", postgres_results)
        PostgreSQLConnection.save_postgres_results(postgres_query_stats, "postgres_results")
    finally:
        postgres_conn.close()


if __name__ == "__main__":
    main()