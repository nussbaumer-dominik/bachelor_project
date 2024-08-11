import argparse
import csv
import os
import random
import subprocess
import time

import networkx as nx
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm

from postgres_connection import PostgreSQLConnection

# Load environment variables
load_dotenv(find_dotenv(), override=True)

# Database configurations
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_IMPORT_PATH = os.getenv('NEO4J_IMPORT_PATH')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
CONTAINER_NAME = "lsqb-neo"


# def generate_graph(num_nodes, avg_friendships):
#     g = nx.Graph()
#     g.add_nodes_from(range(num_nodes))
#
#     for node in g.nodes():
#         num_edges = min(avg_friendships, num_nodes - 1)
#         potential_friends = list(set(g.nodes()) - set(g.neighbors(node)) - {node})
#         if num_edges > len(potential_friends):
#             num_edges = len(potential_friends)
#         friends = random.sample(potential_friends, num_edges)
#         for friend in friends:
#             g.add_edge(node, friend)
#
#     return g

def generate_graph(num_nodes, max_friendships):
    g = nx.Graph()
    g.add_nodes_from(range(num_nodes))

    for node in g.nodes():
        num_edges = min(max_friendships, num_nodes - 1)  # Use min to ensure we don't exceed the max friendships
        potential_friends = list(set(g.nodes()) - set(g.neighbors(node)) - {node})
        if num_edges > len(potential_friends):
            num_edges = len(potential_friends)
        friends = random.sample(potential_friends, num_edges)
        for friend in friends:
            g.add_edge(node, friend)

    return g


def restart_neo4j():
    try:
        subprocess.run(f'docker restart {CONTAINER_NAME}', shell=True, check=True)
        print("Neo4j restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Neo4j restart: {e}")


def import_graph_to_neo4j():
    command = (
        f'docker exec {CONTAINER_NAME} neo4j-admin database import full --delimiter="," '
        f"--nodes=Person=import/nodes.csv "
        f"--relationships=KNOWS=import/edges.csv "
        "--overwrite-destination"
    )
    try:
        subprocess.run(command, shell=True, check=True)
        print("Neo4j import successful.")
        restart_neo4j()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Neo4j import: {e}")


def export_graph_to_csv(g):
    with open(f'{NEO4J_IMPORT_PATH}/nodes.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id:ID(Person)"])
        for node in g.nodes():
            writer.writerow([node])

    with open(f'{NEO4J_IMPORT_PATH}/edges.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([":START_ID(Person)", ":END_ID(Person)"])
        for edge in g.edges():
            writer.writerow([edge[0], edge[1]])


def create_graph_in_postgres(g):
    postgres_conn = PostgreSQLConnection(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD)
    try:
        with postgres_conn.conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS person_knows_person;")
            cursor.execute("CREATE TABLE person_knows_person (person1id INT, person2id INT);")

            insert_query = "INSERT INTO person_knows_person (person1id, person2id) VALUES (%s, %s)"
            for edge in tqdm(g.edges(), desc="Inserting relationships into PostgreSQL"):
                cursor.execute(insert_query, (edge[0], edge[1]))
                cursor.execute(insert_query, (edge[1], edge[0]))

            postgres_conn.conn.commit()
    finally:
        postgres_conn.close()


def main(num_nodes, avg_friendships, neo4j, postgres):
    graph_start_time = time.time()
    g = generate_graph(num_nodes, avg_friendships)
    print(f"Graph generated in {time.time() - graph_start_time:.2f} seconds")
    print(f"Generated a graph with {num_nodes} nodes and {len(g.edges())} edges")
    if neo4j:
        export_graph_to_csv(g)
        import_graph_to_neo4j()
        print("Graph created in Neo4j database.")

    if postgres:
        create_graph_in_postgres(g)
        print("Graph created in PostgreSQL database.")
    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate a graph and populate it into Neo4j and PostgreSQL databases.')
    parser.add_argument('-n', '--num-nodes', type=int, required=True, help='Number of nodes in the graph')
    parser.add_argument('-f', '--avg-friendships', type=int, required=True,
                        help='Average number of friendships per node')
    parser.add_argument("-nf", "--neo4j", action="store_true", help="Run Neo4j")
    parser.add_argument("-pf", "--postgres", action="store_true", help="Run PostgreSQL")

    args = parser.parse_args()

    main(args.num_nodes, args.avg_friendships, args.neo4j, args.postgres)
