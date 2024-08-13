import csv
import os
import statistics
import time

from psycopg import connect, OperationalError, ProgrammingError
from tqdm import tqdm

from iconnection import IConnection


class PostgreSQLConnection(IConnection):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = connect(host=self.host, port=self.port, user=self.user, password=self.password)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    def run_queries(self, queries, result_dir="postgres_results", runs=5, timeout_seconds=120):
        results = []
        all_query_stats = []

        for idx, (filename, query) in enumerate(queries):
            execution_times = []
            query_errors = []
            rows = []

            for _ in tqdm(range(runs), desc=f"Executing {filename}"):
                try:
                    self.connect()
                    with self.conn.cursor() as cursor:
                        cursor.execute(f"SET statement_timeout TO {timeout_seconds * 1000}")

                        start_time = time.time()
                        cursor.execute(query)
                        rows = cursor.fetchall()
                        end_time = time.time()
                        execution_times.append(end_time - start_time)

                        cursor.execute("SET statement_timeout TO DEFAULT")
                except (OperationalError, ProgrammingError) as e:
                    self.close()
                    query_errors.append(str(e))
                    break
                finally:
                    self.close()

            mean_time = statistics.mean(execution_times) if execution_times else None
            stdev_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            num_records = len(rows) if execution_times else 0

            query_stats = {
                "query_index": idx + 1,
                "filename": filename,
                "result": rows,
                "mean_execution_time_s": mean_time,
                "std_dev_time_s": stdev_time,
                "num_records": num_records,
                "execution_times": execution_times,
                "errors": query_errors
            }
            all_query_stats.append(query_stats)
            results.append({"data": rows if execution_times else []})

        self.save_postgres_results(all_query_stats, result_dir)
        return results, all_query_stats

    @staticmethod
    def save_postgres_results(all_results, result_dir):
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        filename = f"{result_dir}/postgres_query_summary.csv"
        with open(filename, "w", newline="") as file:
            fieldnames = ['query_index', 'filename', 'result', 'mean_execution_time_s', 'std_dev_time_s', 'num_records',
                          'errors']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for result in all_results:
                row = {key: result[key] for key in result if key in fieldnames}
                row['errors'] = str(result['errors'])
                writer.writerow(row)
