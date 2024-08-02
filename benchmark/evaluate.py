import matplotlib.pyplot as plt
import pandas as pd

NEO4J_DIR = "neo4j_results"
POSTGRES_DIR = "postgres_results"


def verify_results(num_queries):
    identical = True
    for i in range(1, num_queries + 1):
        neo4j_df = pd.read_csv(f'neo4j_query_{i}_results.csv')
        postgres_df = pd.read_csv(f'postgres_query_{i}_results.csv')
        print(neo4j_df)
        print(postgres_df)

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


def evaluate_foaf_results():
    neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_foaf_summary.csv')
    postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_foaf_summary.csv')
    if len(neo4j_df) != len(postgres_df):
        print("Number of queries differ between Neo4j and PostgreSQL.")
        return

    # Check the result column format and compare
    for i in range(len(neo4j_df)):
        # Process Neo4j results
        neo4j_result_raw = neo4j_df.loc[i, 'result']
        # Assuming the result is stored as a string representation of a list of dicts
        neo4j_result_processed = [entry['person2id'] for entry in eval(neo4j_result_raw)]

        # Process PostgreSQL results
        postgres_result_raw = postgres_df.loc[i, 'result']
        # Assuming the result is stored as a string representation of a list of tuples
        postgres_result_processed = [entry[0] for entry in eval(postgres_result_raw)]

        # Compare the results
        if set(neo4j_result_processed) != set(postgres_result_processed):
            print(f"Mismatch found for query {i + 1}")
            print(f"Difference: {set(neo4j_result_processed) ^ set(postgres_result_processed)}")
        else:
            print(f"Results match for query {i + 1}")


def evaluate_lsqb():
    neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_query_summary.csv')
    postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_query_summary.csv')

    # Make sure the data is comparable
    if len(neo4j_df) != len(postgres_df):
        print("Number of queries differ between Neo4j and PostgreSQL.")
        return

    # Extract mean execution times and standard deviations
    neo4j_means = neo4j_df['mean_execution_time_s']
    neo4j_std_devs = neo4j_df['std_dev_time_s']
    postgres_means = postgres_df['mean_execution_time_s']
    postgres_std_devs = postgres_df['std_dev_time_s']

    speed_diff_percent = ((postgres_means - neo4j_means) / neo4j_means) * 100

    # Set up the figure to accommodate individual subplots for each query
    num_queries = len(neo4j_means)
    fig, axes = plt.subplots(num_queries, 1, figsize=(10, 6 * num_queries))

    for i in range(num_queries):
        ax = axes[i] if num_queries > 1 else axes
        index = [0, 1]  # Positions for Neo4j and PostgreSQL bars
        means = [neo4j_means[i], postgres_means[i]]
        std_devs = [neo4j_std_devs[i], postgres_std_devs[i]]
        bar_labels = ['Neo4j', 'PostgreSQL']

        # Plotting for the current query
        ax.bar(index, means, yerr=std_devs, align='center', alpha=0.7, ecolor='black', capsize=10)
        ax.set_ylabel('Mean Execution Time (s)')
        ax.set_title(f'Query {i + 1} Execution Time Comparison')
        ax.set_xticks(index)
        ax.set_xticklabels(bar_labels)
        ax.set_xlabel('Database')
        ax.yaxis.grid(True)  # Add horizontal grid lines

    plt.tight_layout()
    plt.show()

    # Print speed differences in percentage
    for i in range(len(speed_diff_percent)):
        print(
            f"Query {i + 1}: PostgreSQL is {'faster' if speed_diff_percent[i] < 0 else 'slower'} than Neo4j by {abs(speed_diff_percent[i]):.2f}%")


if __name__ == "__main__":
    evaluate_lsqb()
    # evaluate_foaf_results()
    # num_queries = 5
    # verify_results(num_queries)
