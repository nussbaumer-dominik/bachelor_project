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


def evaluate_fof_across_configurations(configurations):
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

        ax.set_title(f'FOF {query_index} hops')
        ax.set_xlabel('Configurations')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks(indices + bar_width / 2)
        ax.set_xticklabels(configurations)

        if query_index == 1:
            ax.legend([neo4j_bar, postgres_bar], ['Neo4j', 'Postgres'], title="Database", loc='upper left')

    axs[-1].axis('off')
    # plt.plot()
    # plt.savefig('fof-benchmark-results.pdf', format='pdf')
    plt.show()


def evaluate_fof_lsqb_across_scaling_factors(configurations):
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
                neo4j_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-{config}_5-times_fof.csv')
                neo4j_mean = neo4j_df.loc[neo4j_df['query_index'] == query_index, 'mean_execution_time_s'].values[0]
            except Exception as _:
                neo4j_mean = 0

            try:
                neo4j_index_df = pd.read_csv(f'{NEO4J_DIR}/neo4j_lsqb-{config}_5-times_fof-index.csv')
                neo4j_index_mean = \
                    neo4j_index_df.loc[neo4j_index_df['query_index'] == query_index, 'mean_execution_time_s'].values[0]
            except Exception as _:
                neo4j_index_mean = 0

            try:
                postgres_df = pd.read_csv(f'{POSTGRES_DIR}/postgres_lsqb-{config}_5-times_fof.csv')
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

        ax.set_title(f'FOF {query_index} hops')
        ax.set_xlabel('Configurations')
        ax.set_ylabel('Execution Time (s)')
        ax.set_yscale('log')
        ax.set_xticks(base_indices + 1.5 * bar_width)
        ax.set_xticklabels(configurations)

        if query_index == 1:
            ax.legend(['Neo4j', 'Neo4j index', 'Postgres'], title="Database", loc='upper left')

    axs[-1].axis('off')
    # plt.plot()
    # plt.savefig('fof-lsqb-benchmark-results.pdf', format='pdf')
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

            bar1 = ax.bar(index, neo4j_means, bar_width, color=db_colors['Neo4j'], alpha=0.7)
            bar2 = ax.bar(index + bar_width, postgres_means, bar_width, color=db_colors['Postgres'], alpha=0.7)

            for bar, value in zip([bar1, bar2], [neo4j_means.values[0], postgres_means.values[0]]):
                ax.annotate(f'{value:.2f}s',
                            xy=(bar[0].get_x() + bar[0].get_width() / 2, value),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')

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

    plt.plot()
    plt.savefig('lsqb-benchmark-results.pdf', format='pdf')
    plt.show()


def evaluate_shortest_path():
    neo4j_data = pd.read_csv(f'{NEO4J_DIR}/neo4j_shortest_path.csv')
    postgres_data = pd.read_csv(f'{POSTGRES_DIR}/postgres_shortest_path.csv')
    neo4j_data['query_index'] = neo4j_data['query_index'].astype(str)
    postgres_data['query_index'] = postgres_data['query_index'].astype(str)
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
            ax.annotate(f'{height:.2f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax.set_xlabel('Database Size and Configuration')
    ax.set_ylabel('Mean Execution Time (s)')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(merged_data['size_neo4j'])
    ax.legend()
    ax.set_yscale('log')
    ax.yaxis.grid(True, which='major', linestyle='--', linewidth='0.5', color='grey')
    ax.yaxis.grid(False, which='minor')
    plt.tight_layout()
    # plt.plot()
    # plt.savefig('shortest-path-benchmark-results.pdf', format='pdf')
    plt.show()

    postgres_means = postgres_data['mean_execution_time_s']
    neo4j_means = neo4j_data['mean_execution_time_s']
    speed_diff_percent = ((postgres_means - neo4j_means) / neo4j_means) * 100
    for i in range(len(speed_diff_percent)):
        print(
            f"Query {i + 1}: PostgreSQL is {'faster' if speed_diff_percent[i] < 0 else 'slower'} than Neo4j by {abs(speed_diff_percent[i]):.2f}%")

    print(f"Average speed difference: {np.mean(speed_diff_percent):.2f}%")
    print(f"Median speed difference: {np.median(speed_diff_percent):.2f}%")

def evaluate_shortest_path_improved():
    neo4j_data = pd.read_csv(f'{NEO4J_DIR}/neo4j_shortest_path_improved.csv')
    postgres_data = pd.read_csv(f'{POSTGRES_DIR}/postgres_shortest_path_improved.csv')
    neo4j_data['query_index'] = neo4j_data['query_index'].astype(str)
    postgres_data['query_index'] = postgres_data['query_index'].astype(str)
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
            ax.annotate(f'{height:.4f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax.set_xlabel('LSQB Scaling Factor')
    ax.set_ylabel('Mean Execution Time (s)')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(merged_data['size_neo4j'])
    ax.legend(loc='upper left')
    ax.set_yscale('log')
    ax.yaxis.grid(True, which='major', linestyle='--', linewidth='0.5', color='grey')
    ax.yaxis.grid(False, which='minor')
    plt.tight_layout()
    #plt.plot()
    #plt.savefig('shortest-path-optimized-benchmark-results.pdf', format='pdf')
    plt.show()

    postgres_means = postgres_data['mean_execution_time_s']
    neo4j_means = neo4j_data['mean_execution_time_s']
    speed_diff_percent = ((postgres_means - neo4j_means) / neo4j_means) * 100
    for i in range(len(speed_diff_percent)):
        print(
            f"Query {i + 1}: PostgreSQL is {'faster' if speed_diff_percent[i] < 0 else 'slower'} than Neo4j by {abs(speed_diff_percent[i]):.2f}%")

    print(f"Average speed difference: {np.mean(speed_diff_percent):.2f}%")
    print(f"Median speed difference: {np.median(speed_diff_percent):.2f}%")


def plot_execution_time_vs_scaling_factor():
    neo4j_data = pd.read_csv(f'{NEO4J_DIR}/neo4j_shortest_path_increase.csv')
    postgres_data = pd.read_csv(f'{POSTGRES_DIR}/postgres_shortest_path_increase.csv')
    sf_neo4j = neo4j_data['SF'].astype(str)
    time_neo4j = neo4j_data['mean_execution_time_s']
    edges_neo4j = neo4j_data['edges']

    sf_postgres = postgres_data['SF'].astype(str)
    time_postgres = postgres_data['mean_execution_time_s']

    fig, ax1 = plt.subplots(figsize=(10, 4))

    ax1.set_xlabel('Scaling Factor (SF)')
    ax1.set_ylabel('Mean Execution Time (s)')
    ax1.plot(sf_neo4j, time_neo4j, label='Neo4j Execution Time', marker='o', linestyle='-', color=db_colors['Neo4j'])
    ax1.plot(sf_postgres, time_postgres, label='PostgreSQL Execution Time', marker='o', linestyle='-',
             color=db_colors['Postgres'])
    ax1.set_yscale('log')
    ax1.tick_params(axis='y')

    for i, sf in enumerate(sf_neo4j):
        y_offset = time_neo4j[i] * 1.2
        if sf == '1':
            y_offset = max(time_postgres[i] * 1.2, edges_neo4j[i] * 1.1)

        factor = "1x" if i == 0 else f"{(time_neo4j[i] / time_neo4j[i - 1]):.2f}x"
        if i == 0:
            ax1.text(i, y_offset, f'{time_neo4j[i]:.3f}s', ha='center', color=db_colors['Neo4j'])
        else:
            ax1.text(i, y_offset, f'{time_neo4j[i]:.3f}s\n({factor})', ha='center', color=db_colors['Neo4j'])

    for i in range(len(time_postgres)):
        factor = "1x" if i == 0 else f"{(time_postgres[i] / time_postgres[i - 1]):.2f}x"
        y_offset = time_postgres[i] * 1.2
        if i == 0:
            ax1.text(i, y_offset, f'{time_postgres[i]:.2f}s', ha='center', color=db_colors['Postgres'])
        else:
            ax1.text(i, y_offset, f'{time_postgres[i]:.2f}s\n({factor})', ha='center', color=db_colors['Postgres'])

    ax2 = ax1.twinx()
    ax2.set_ylabel('Number of "KNOWS" relations')
    ax2.plot(sf_neo4j, edges_neo4j, label='Number of "KNOWS" relations', marker='s', linestyle='--', color='red')
    ax2.tick_params(axis='y')

    for i, sf in enumerate(sf_neo4j):
        y_offset = edges_neo4j[i] * 1.1
        if sf == '0.1':
            y_offset = time_neo4j[i] * 1.3
        elif sf == '1':
            y_offset = time_postgres[i]

        factor = "1x" if i == 0 else f"{(edges_neo4j[i] / edges_neo4j[i - 1]):.2f}x"
        if i > 0:
            ax2.text(i, y_offset, f'{factor}', ha='center', color='red')

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    ax1.grid(True)
    plt.tight_layout()
    # plt.plot()
    # plt.savefig('sp-increase.pdf', format='pdf')
    plt.show()


if __name__ == "__main__":
    # evaluate_lsqb(show_whiskers=False)
    # evaluate_queries_across_scaling_factors([0.1, 0.3, 1])
    # evaluate_fof_across_configurations(["100K-50reg", "50K-100reg", "1M-5reg", "1M-10reg", "1M-20reg"])
    # evaluate_fof_lsqb_across_scaling_factors(["0.1", "0.3", "1"])
    #evaluate_shortest_path()
    evaluate_shortest_path_improved()
    # plot_execution_time_vs_scaling_factor()
