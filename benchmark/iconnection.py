class IConnection:
    def close(self):
        """Close the connection to the database."""
        pass

    def run_queries(self, queries, result_dir="postgres_results"):
        """Run the queries and return the results and query statistics."""
        pass
