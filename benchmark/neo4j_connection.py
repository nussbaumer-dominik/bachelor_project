import csv
import os
import statistics
import time

import neo4j.exceptions
from neo4j import GraphDatabase, Query
from tqdm import tqdm


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_queries(self, queries, result_dir="neo4j_results", runs=5, timeout_seconds=120):
        results = []
        all_query_stats = []
        for idx, (filename, query_string) in enumerate(queries):
            execution_times = []
            query_errors = []
            data = []
            with self.driver.session() as session:
                for _ in tqdm(range(runs), desc=f"Executing {filename}"):
                    try:
                        start_time = time.time()
                        query = Query(query_string, timeout=timeout_seconds)
                        result = session.run(query)
                        data = result.data()
                        end_time = time.time()
                        execution_times.append(end_time - start_time)
                    except neo4j.exceptions.Neo4jError as e:
                        query_errors.append(str(e))
                        break

            mean_time = statistics.mean(execution_times) if execution_times else None
            stdev_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            num_records = len(data) if data else 0

            query_stats = {
                "query_index": idx + 1,
                "filename": filename,
                "result": data,
                "mean_execution_time_s": mean_time,
                "std_dev_time_s": stdev_time,
                "num_records": num_records,
                "execution_times": execution_times,
                "errors": query_errors
            }

            all_query_stats.append(query_stats)
            results.append({"data": data if data else []})
        self.save_all_query_stats(all_query_stats, result_dir)
        return results, all_query_stats

    @staticmethod
    def save_all_query_stats(all_results, result_dir):
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        filename = f"{result_dir}/neo4j_query_summary.csv"
        with open(filename, "w", newline="") as file:
            fieldnames = ['query_index', "filename", "result", 'mean_execution_time_s', 'std_dev_time_s', 'num_records',
                          'errors']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for result in all_results:
                row = {key: result[key] for key in result if key in fieldnames}
                row['errors'] = str(result['errors'])  # Convert list of errors to string if there are any
                writer.writerow(row)
