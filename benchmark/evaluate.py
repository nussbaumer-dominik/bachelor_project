import matplotlib.pyplot as plt

plt.style.use("default")
import numpy as np
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

    for i in range(len(neo4j_df)):
        neo4j_result_raw = neo4j_df.loc[i, 'result']
        neo4j_result_processed = [entry['person2id'] for entry in eval(neo4j_result_raw)]

        postgres_result_raw = postgres_df.loc[i, 'result']
        postgres_result_processed = [entry[0] for entry in eval(postgres_result_raw)]

        if set(neo4j_result_processed) != set(postgres_result_processed):
            print(f"Mismatch found for query {i + 1}")
            print(f"Difference: {set(neo4j_result_processed) ^ set(postgres_result_processed)}")
        else:
            print(f"Results match for query {i + 1}")


def evaluate_lsqb(show_whiskers=True):
    neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-1_5-times_summary.csv')
    postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_lsqb-1_5-times_summary.csv')

    if len(neo4j_df) != len(postgres_df):
        print("Number of queries differ between Neo4j and PostgreSQL.")
        return

    neo4j_means = neo4j_df['mean_execution_time_s']
    postgres_means = postgres_df['mean_execution_time_s']
    neo4j_std_devs = neo4j_df['std_dev_time_s']
    postgres_std_devs = postgres_df['std_dev_time_s']

    num_queries = len(neo4j_means)
    index = np.arange(num_queries) * 3
    bar_width = 0.8

    fig, ax = plt.subplots(figsize=(12, 4))
    if show_whiskers:
        bars1 = ax.bar(index, neo4j_means, bar_width, yerr=neo4j_std_devs, label='Neo4j', capsize=5, alpha=0.7)
        bars2 = ax.bar(index + bar_width, postgres_means, bar_width, yerr=postgres_std_devs, label='PostgreSQL',
                       capsize=5, alpha=0.7)
    else:
        bars1 = ax.bar(index, neo4j_means, bar_width, label='Neo4j', alpha=0.7)
        bars2 = ax.bar(index + bar_width, postgres_means, bar_width, label='PostgreSQL', alpha=0.7)

    # Add execution times on top of bars
    for bar in bars1:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom', fontsize=8)

    for bar in bars2:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Queries')
    ax.set_ylabel('Mean Execution Time (s)')
    ax.set_title('Execution Time Comparison Across Queries')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels([f'Query {i + 1}' for i in range(num_queries)], fontsize=9)
    ax.legend()

    # Add horizontal grid lines for better readability
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.7)

    plt.tight_layout()
    plt.show()

    # Calculate and print the percentage difference in speed
    speed_diff_percent = ((postgres_means - neo4j_means) / neo4j_means) * 100
    for i in range(len(speed_diff_percent)):
        print(
            f"Query {i + 1}: PostgreSQL is {'faster' if speed_diff_percent[i] < 0 else 'slower'} than Neo4j by {abs(speed_diff_percent[i]):.2f}%")


def evaluate_foaf_across_configurations(configurations):
    num_queries = 9
    fig, axs = plt.subplots(3, 3, figsize=(18, 12), constrained_layout=True)
    axs = axs.flatten()
    bar_width = 0.7
    db_colors = {'Neo4j': 'tab:blue', 'Postgres': 'tab:orange'}

    for query_index in range(1, num_queries + 1):
        ax = axs[query_index - 1]
        ticks = []

        for i, config in enumerate(configurations):
            neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_{config}_summary.csv')
            postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_{config}_summary.csv')

            neo4j_means = neo4j_df.loc[neo4j_df['query_index'] == query_index, 'mean_execution_time_s']
            postgres_means = postgres_df.loc[postgres_df['query_index'] == query_index, 'mean_execution_time_s']

            index = np.arange(1) * len(configurations) + i
            ticks.append(index * bar_width * 2)

            ax.bar(index * 2, neo4j_means, bar_width, label='Neo4j' if i == 0 else "", color=db_colors['Neo4j'],
                   alpha=0.7)
            ax.bar(index * 2 + bar_width, postgres_means, bar_width, label='Postgres' if i == 0 else "",
                   color=db_colors['Postgres'], alpha=0.7)

        ax.set_title(f'FOAF Query {query_index}')
        ax.set_xlabel('Configurations')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks([x * 2 + bar_width / 2 for x in range(len(configurations))])
        ax.set_xticklabels(configurations)
        if query_index == 1:
            ax.legend(title="Database")

    plt.show()


def evaluate_queries_across_scaling_factors(scaling_factors):
    num_queries = 9
    fig, axs = plt.subplots(3, 3, figsize=(15, 15), constrained_layout=True)
    axs = axs.flatten()

    bar_width = 0.7
    db_colors = {'Neo4j': 'tab:blue', 'Postgres': 'tab:orange'}

    for query_index in range(1, num_queries + 1):
        ax = axs[query_index - 1]
        ticks = []

        for i, scaling_factor in enumerate(scaling_factors):
            neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-{scaling_factor}_5-times_summary.csv')
            postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_lsqb-{scaling_factor}_5-times_summary.csv')

            neo4j_means = neo4j_df.loc[neo4j_df['query_index'] == query_index, 'mean_execution_time_s']
            postgres_means = postgres_df.loc[postgres_df['query_index'] == query_index, 'mean_execution_time_s']

            index = np.arange(1) * len(scaling_factors) + i
            ticks.append(index * bar_width * 2)

            ax.bar(index * 2, neo4j_means, bar_width, label='Neo4j' if i == 0 else "", color=db_colors['Neo4j'],
                   alpha=0.7)
            ax.bar(index * 2 + bar_width, postgres_means, bar_width, label='Postgres' if i == 0 else "",
                   color=db_colors['Postgres'], alpha=0.7)

        ax.set_title(f'Query {query_index}')
        ax.set_xlabel('Scaling Factors')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks([x * 2 + bar_width / 2 for x in range(len(scaling_factors))])
        ax.set_xticklabels([f'{sf}' for sf in scaling_factors])
        if query_index == 1:
            ax.legend(title="Database")

    plt.show()


# def evaluate_lsqb():
#     neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-0.1_10-times_summary.csv')
#     postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_lsqb-0.1_10-times_summary.csv')
#
#     if len(neo4j_df) != len(postgres_df):
#         print("Number of queries differ between Neo4j and PostgreSQL.")
#         return
#
#     neo4j_means = neo4j_df['mean_execution_time_s']
#     neo4j_std_devs = neo4j_df['std_dev_time_s']
#     postgres_means = postgres_df['mean_execution_time_s']
#     postgres_std_devs = postgres_df['std_dev_time_s']
#
#     speed_diff_percent = ((postgres_means - neo4j_means) / neo4j_means) * 100
#
#     num_queries = len(neo4j_means)
#     fig, ax = plt.subplots(figsize=(10, 8))
#     index = np.arange(num_queries)
#     bar_width = 0.2
#
#     ax.bar(index - bar_width / 2, neo4j_means, bar_width, label='Neo4j', yerr=neo4j_std_devs, capsize=5)
#     ax.bar(index + bar_width / 2, postgres_means, bar_width, label='PostgreSQL', yerr=postgres_std_devs,
#            capsize=5)
#
#     ax.set_ylabel('Mean Execution Time (s)')
#     ax.set_title('Execution Time Comparison by Query and Database')
#     ax.set_xticks(index)
#     ax.set_xticklabels([f'Query {i + 1}' for i in range(num_queries)])
#     ax.legend()
#     ax.yaxis.grid(True)
#
#     plt.tight_layout()
#     plt.show()
#
#     for i in range(len(speed_diff_percent)):
#         print(
#             f"Query {i + 1}: PostgreSQL is {'faster' if speed_diff_percent[i] < 0 else 'slower'} than Neo4j by {abs(speed_diff_percent[i]):.2f}%")


if __name__ == "__main__":
    # evaluate_lsqb(show_whiskers=False)
    # evaluate_queries_across_scaling_factors([0.1, 0.3, 1])
    evaluate_foaf_across_configurations(["1M-5regular", "1M-10regular", "1M-20regular", "100K-50regular"])
    # evaluate_foaf_results()
    # num_queries = 5
    # verify_results(num_queries)
