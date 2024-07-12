import pandas as pd
import os

def verify_results(num_queries):
    identical = True
    for i in range(1, num_queries + 1):
        neo4j_df = pd.read_csv(f'neo4j_query_{i}_results.csv')
        postgres_df = pd.read_csv(f'postgres_query_{i}_results.csv')

        if not neo4j_df.equals(postgres_df):
            try:
                neo4j_df = neo4j_df.sort_values(by=list(neo4j_df.columns)).reset_index(drop=True)
                postgres_df = postgres_df.sort_values(by=list(postgres_df.columns)).reset_index(drop=True)
            except Exception:
                pass

            # Check again after sorting
            if not neo4j_df.equals(postgres_df):
                identical = False
                print(f'Results for Query {i} differ between Neo4j and PostgreSQL.')

    if identical:
        print('All query results are identical between Neo4j and PostgreSQL.')
    else:
        print('There are differences in the query results between the two databases.')

if __name__ == "__main__":
    num_queries = 2  # Adjust this based on how many queries you are running
    verify_results(num_queries)
