import csv
import os
import time

from psycopg import connect


class PostgreSQLConnection:
    def __init__(self, host, port, user, password):
        self.conn = connect(host=host, port=port, user=user, password=password)

    def close(self):
        self.conn.close()

    def run_queries(self, queries, result_dir="postgres_results"):
        results = []
        all_query_stats = []
        with self.conn.cursor() as cursor:
            for idx, (filename, query) in enumerate(queries):
                print(f"Running PostgreSQL query {filename}")
                start_time = time.time()
                cursor.execute(query)
                end_time = time.time()
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                dict_rows = [{column: value for column, value in zip(columns, row)} for row in rows]

                query_stats = {
                    "query_index": idx + 1,
                    "query_filename": filename,
                    "execution_time_s": end_time - start_time,
                    "rows": dict_rows,
                    "query_plan": cursor.query_plan if hasattr(cursor, 'query_plan') else "N/A",
                    "columns": columns,
                    "num_records": len(rows)
                }
                all_query_stats.append(query_stats)
                results.append({"data": dict_rows})
                save_query_results(dict_rows, result_dir, f"postgres_{filename}_result", columns)

        return results, all_query_stats

    @staticmethod
    def save_postgres_results(all_results, result_dir="results"):
        fieldnames = ['query_index', "query_filename", 'execution_time_s', 'query_plan', 'columns', 'num_records',
                      'rows']
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        with open(f"{result_dir}/postgres_query_summary.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for result in all_results:
                # Flatten the 'rows' data if it's not needed as a dictionary in the CSV
                result["rows"] = str(
                    result["rows"])  # Convert list of dicts to string if preserving structure is needed
                writer.writerow(result)

def save_query_results(data, result_dir: str, filename: str = None, headers: list[str] = None):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    with open(f"{result_dir}/{filename}.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)