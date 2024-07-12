import csv
import os
import time

from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase
from psycopg import connect

load_dotenv(find_dotenv(), override=True)

# Database configurations
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
POSTGRES_URI = os.getenv('POSTGRES_URI')
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
                queries.append(query)
    return queries


def run_neo4j_queries(queries: list):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    results = []
    all_query_stats = []
    with driver.session() as session:
        for idx, query in enumerate(queries):
            start_time = time.time()
            result = session.run(query)
            data = result.data()  # Fetch data before consuming
            result_summary = result.consume()
            end_time = time.time()

            query_time = end_time - start_time
            available_after = result_summary.result_available_after
            consumed_after = result_summary.result_consumed_after

            # Collect statistics for each query
            query_stats = {
                "query_index": idx + 1,
                "execution_time": query_time,
                "available_after": available_after,
                "consumed_after": consumed_after,
                "num_records": len(data)
            }
            all_query_stats.append(query_stats)

            results.append({"data": data})

            save_query_results(idx + 1, data)

    driver.close()
    return results, all_query_stats


def run_postgres_queries_and_save(queries):
    with connect(POSTGRES_URI) as conn:
        with conn.cursor() as cursor:
            results = []
            for idx, query in enumerate(queries):
                start_time = time.time()
                cursor.execute(query)
                end_time = time.time()
                query_time = end_time - start_time
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                results.append({"rows": rows, "execution_time": query_time,
                                "query_plan": cursor.query_plan if hasattr(cursor, 'query_plan') else "N/A"})
                with open(f'postgres_query_{idx + 1}_results.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(columns + ['execution_time'])
                    for row in rows:
                        writer.writerow(list(row) + [query_time])
    return results


def save_query_results(query_index, data):
    filename = f'neo4j_query_{query_index}_results.csv'
    fieldnames = []
    if data:
        sample_row = data[0]
        fieldnames = list(sample_row.keys())

    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def save_all_query_stats(all_results):
    with open('neo4j_query_summary.csv', 'w', newline='') as file:
        fieldnames = ['query_index', 'execution_time', 'available_after', 'consumed_after', 'num_records']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)


def main():
    neo4j_queries = read_queries(NEO4J_QUERY_DIR, '.cypher')
    postgres_queries = read_queries(POSTGRES_QUERY_DIR, '.sql')
    neo4j_results, neo4j_query_stats = run_neo4j_queries(neo4j_queries)
    save_all_query_stats(neo4j_query_stats)
    # run_postgres_queries_and_save(postgres_queries)


if __name__ == "__main__":
    main()
