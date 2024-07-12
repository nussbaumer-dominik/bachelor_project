import csv
import os
import time

from neo4j import GraphDatabase

from iconnection import IConnection


class Neo4jConnection(IConnection):
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_queries(self, queries, result_dir="neo4j_results"):
        results = []
        all_query_stats = []
        with self.driver.session() as session:
            for idx, (filename, query) in enumerate(queries):
                print(f"Running Neo4j query {filename}")
                start_time = time.time()
                result = session.run(query)
                data = result.data()
                result_summary = result.consume()
                end_time = time.time()

                query_stats = {
                    "query_index": idx + 1,
                    "query_filename": filename,
                    "execution_time_s": end_time - start_time,
                    "available_after_ms": result_summary.result_available_after,
                    "consumed_after_ms": result_summary.result_consumed_after,
                    "num_records": len(data)
                }
                all_query_stats.append(query_stats)
                results.append({"data": data})
                save_query_results(data, result_dir, f"neo4j_{filename}_result", ["count"])

        return results, all_query_stats

    @staticmethod
    def save_all_query_stats(all_results: list, result_dir: str):
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        with open(f"{result_dir}/neo4j_query_summary.csv", "w", newline="") as file:
            fieldnames = ['query_index', "query_filename", 'execution_time_s', 'available_after_ms',
                          'consumed_after_ms',
                          'num_records']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)


def save_query_results(data, result_dir: str, filename: str = None, headers: list[str] = None):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    with open(f"{result_dir}/{filename}.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
