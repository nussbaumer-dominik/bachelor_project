import matplotlib.pyplot as plt

plt.style.use("default")
import numpy as np
import pandas as pd

NEO4J_DIR = "neo4j_results"
POSTGRES_DIR = "postgres_results"
db_colors = {'Neo4j': 'tab:blue', 'Neo4j-index': 'tab:cyan', 'Postgres': 'tab:orange'}


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

    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.7)

    plt.tight_layout()
    plt.show()

    speed_diff_percent = ((postgres_means - neo4j_means) / neo4j_means) * 100
    for i in range(len(speed_diff_percent)):
        print(
            f"Query {i + 1}: PostgreSQL is {'faster' if speed_diff_percent[i] < 0 else 'slower'} than Neo4j by {abs(speed_diff_percent[i]):.2f}%")


def evaluate_foaf_across_configurations(configurations):
    num_queries = 8
    fig, axs = plt.subplots(3, 3, figsize=(15, 15), constrained_layout=True)
    axs = axs.flatten()
    bar_width = 0.7

    for query_index in range(1, num_queries + 1):
        ax = axs[query_index - 1]
        neo4j_line_data = []
        postgres_line_data = []

        for i, config in enumerate(configurations):
            neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_{config}_summary.csv')
            postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_{config}_summary.csv')

            neo4j_means = neo4j_df.loc[neo4j_df['query_index'] == query_index, 'mean_execution_time_s']
            postgres_means = postgres_df.loc[postgres_df['query_index'] == query_index, 'mean_execution_time_s']

            neo4j_line_data.append(neo4j_means.values[0] if not neo4j_means.empty else None)
            postgres_line_data.append(postgres_means.values[0] if not postgres_means.empty else None)

            index = np.arange(1) * len(configurations) + i * 2 + (bar_width / 2)
            neo4j_bar = ax.bar(index, neo4j_means, bar_width, label='Neo4j' if i == 0 else "", color=db_colors['Neo4j'],
                               alpha=0.7)
            postgres_bar = ax.bar(index + bar_width, postgres_means, bar_width, label='Postgres' if i == 0 else "",
                                  color=db_colors['Postgres'], alpha=0.7)

        indices = np.array(range(len(configurations))) * 2 + bar_width / 2
        ax.plot(indices, neo4j_line_data, '-', marker='^', color=db_colors['Neo4j'])
        ax.plot(indices + bar_width, postgres_line_data, '-', marker='s', color=db_colors['Postgres'])

        ax.set_title(f'FOAF {query_index} hops')
        ax.set_xlabel('Configurations')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks(indices + bar_width / 2)
        ax.set_xticklabels(configurations)

        if query_index == 1:
            ax.legend([neo4j_bar, postgres_bar], ['Neo4j', 'Postgres'], title="Database", loc='upper left')

    axs[-1].axis('off')

    plt.show()


def evaluate_foaf_lsqb_across_scaling_factors(configurations):
    num_queries = 8
    fig, axs = plt.subplots(3, 3, figsize=(15, 15), constrained_layout=True)
    axs = axs.flatten()
    bar_width = 0.2

    group_spacing = 0.5

    for query_index in range(1, num_queries + 1):
        ax = axs[query_index - 1]
        neo4j_line_data = []
        neo4j_index_line_data = []
        postgres_line_data = []

        base_indices = np.arange(len(configurations)) * (3 * bar_width + group_spacing)

        for i, config in enumerate(configurations):
            try:
                neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-{config}_5-times_foaf.csv')
                neo4j_mean = neo4j_df.loc[neo4j_df['query_index'] == query_index, 'mean_execution_time_s'].values[0]
            except Exception as _:
                neo4j_mean = 0

            try:
                neo4j_index_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-{config}_5-times_foaf-index.csv')
                neo4j_index_mean = \
                    neo4j_index_df.loc[neo4j_index_df['query_index'] == query_index, 'mean_execution_time_s'].values[0]
            except Exception as _:
                neo4j_index_mean = 0

            try:
                postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_lsqb-{config}_5-times_foaf.csv')
                postgres_mean = \
                    postgres_df.loc[postgres_df['query_index'] == query_index, 'mean_execution_time_s'].values[0]
            except Exception as _:
                postgres_mean = 0

            neo4j_line_data.append(neo4j_mean)
            neo4j_index_line_data.append(neo4j_index_mean)
            postgres_line_data.append(postgres_mean)

            ax.bar(base_indices[i], neo4j_mean, bar_width, color=db_colors['Neo4j'], alpha=0.7)
            ax.bar(base_indices[i] + bar_width, neo4j_index_mean, bar_width, color=db_colors['Neo4j-index'], alpha=0.7)
            ax.bar(base_indices[i] + 2 * bar_width, postgres_mean, bar_width, color=db_colors['Postgres'], alpha=0.7)

        ax.plot(base_indices, neo4j_line_data, '-', marker='^', color=db_colors['Neo4j'])
        ax.plot(base_indices + bar_width, neo4j_index_line_data, '-', marker='^', color=db_colors['Neo4j-index'])
        ax.plot(base_indices + 2 * bar_width, postgres_line_data, '-', marker='s', color=db_colors['Postgres'])

        ax.set_title(f'FOAF {query_index} hops')
        ax.set_xlabel('Configurations')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks(base_indices + 1.5 * bar_width)
        ax.set_xticklabels(configurations)

        if query_index == 1:
            ax.legend(['Neo4j', 'Neo4j index', 'Postgres'], title="Database", loc='upper left')

    axs[-1].axis('off')

    plt.show()


def evaluate_queries_across_scaling_factors(scaling_factors):
    num_queries = 9
    fig, axs = plt.subplots(3, 3, figsize=(15, 15), constrained_layout=True)
    axs = axs.flatten()

    bar_width = 0.7
    db_colors = {'Neo4j': 'tab:blue', 'Postgres': 'tab:orange'}

    for query_index in range(1, num_queries + 1):
        ax = axs[query_index - 1]
        neo4j_line_data = []
        postgres_line_data = []
        indices = []

        for i, scaling_factor in enumerate(scaling_factors):
            neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-{scaling_factor}_5-times_summary.csv')
            postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_lsqb-{scaling_factor}_5-times_summary.csv')

            neo4j_means = neo4j_df.loc[neo4j_df['query_index'] == query_index, 'mean_execution_time_s']
            postgres_means = postgres_df.loc[postgres_df['query_index'] == query_index, 'mean_execution_time_s']

            neo4j_line_data.append(neo4j_means.values[0] if not neo4j_means.empty else None)
            postgres_line_data.append(postgres_means.values[0] if not postgres_means.empty else None)

            index = i * 2 * (bar_width + 0.1)
            indices.append(index)

            ax.bar(index, neo4j_means, bar_width, color=db_colors['Neo4j'], alpha=0.7)
            ax.bar(index + bar_width, postgres_means, bar_width, color=db_colors['Postgres'], alpha=0.7)

        ax.plot(indices, neo4j_line_data, '-', marker='^', color=db_colors['Neo4j'],
                label='Neo4j Trend' if query_index == 1 else "")
        ax.plot([x + bar_width for x in indices], postgres_line_data, '-', marker='s', color=db_colors['Postgres'],
                label='Postgres Trend' if query_index == 1 else "")

        ax.set_title(f'Q{query_index}')
        ax.set_xlabel('Scaling Factors')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks([x + bar_width / 2 for x in indices])
        ax.set_xticklabels([f'{sf}' for sf in scaling_factors])

        if query_index == 1:
            ax.legend([ax.bar(0, 0, color=db_colors['Neo4j'], alpha=0.7),
                       ax.bar(0, 0, color=db_colors['Postgres'], alpha=0.7)],
                      ['Neo4j', 'Postgres'], title="Database")

    plt.show()


def evaluate_shortest_path():
    neo4j_data = pd.read_csv(f'{NEO4J_DIR}/neo4j_shortest_path.csv')
    neo4j_data['query_index'] = neo4j_data['query_index'].astype(str)

    postgres_data = pd.read_csv(f'{POSTGRES_DIR}/postgres_shortest_path.csv')
    postgres_data.columns = ['query_index', 'size', 'mean_execution_time_s', 'std_dev_time_s', 'errors']
    postgres_data['query_index'] = postgres_data['query_index'].map({
        '100K-50reg': '1', '50K-100reg': '2', '1M-5reg': '3',
        '1M-10reg': '4', '1M-20reg': '5', 'SF0.1': '6',
        'SF0.3': '7', 'SF1': '8'
    })

    merged_data = pd.merge(neo4j_data, postgres_data, on='query_index', suffixes=('_neo4j', '_postgres'))

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.35
    index = np.arange(len(merged_data))

    bars_neo4j = ax.bar(index, merged_data['mean_execution_time_s_neo4j'], bar_width, label='Neo4j',
                        color=db_colors['Neo4j'])
    bars_postgres = ax.bar(index + bar_width, merged_data['mean_execution_time_s_postgres'], bar_width,
                           label='Postgres', color=db_colors['Postgres'])

    for bars in [bars_neo4j, bars_postgres]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height:.2f}s',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom'
            )

    ax.set_xlabel('Database Size and Configuration')
    ax.set_ylabel('Mean Execution Time (s)')
    ax.set_title('Comparison of Shortest Path Mean Execution Times for Neo4j and Postgres (Log Scale)')
    ax.set_xticks(index + bar_width / 2, merged_data['size_neo4j'])
    ax.legend()
    ax.set_yscale('log')
    ax.yaxis.grid(True, which='major', linestyle='--', linewidth='0.3', color='grey')
    ax.yaxis.grid(False, which='minor')

    plt.show()


if __name__ == "__main__":
    # evaluate_lsqb(show_whiskers=False)
    # evaluate_queries_across_scaling_factors([0.1, 0.3, 1])
    # evaluate_foaf_across_configurations(["100K-50reg", "50K-100reg", "1M-5reg", "1M-10reg", "1M-20reg"])
    # evaluate_foaf_lsqb_across_scaling_factors(["0.1", "0.3", "1"])
    evaluate_shortest_path()
