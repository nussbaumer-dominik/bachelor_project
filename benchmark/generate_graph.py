import argparse
import csv
import os
import subprocess
import time

import networkx as nx
from dotenv import load_dotenv, find_dotenv

from postgres_connection import PostgreSQLConnection

load_dotenv(find_dotenv(), override=True)

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_IMPORT_PATH = os.getenv('NEO4J_IMPORT_PATH')
NEO4J_CONTAINER_NAME = "lsqb-neo"
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')


def generate_regular_graph(n: int, degree: int) -> nx.Graph:
    return nx.random_regular_graph(degree, n)


def restart_neo4j():
    try:
        subprocess.run(f'docker restart {NEO4J_CONTAINER_NAME}', shell=True, check=True)
        print("Neo4j restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Neo4j restart: {e}")


def import_graph_to_neo4j():
    command = (
        f'docker exec {NEO4J_CONTAINER_NAME} neo4j-admin database import full --delimiter="," '
        "--id-type=INTEGER "
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


def export_graph_to_csv(g: nx.Graph, neo4j: bool, postgres: bool):
    if neo4j:
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


def bulk_import_to_postgres(g: nx.Graph, table_name: str):
    postgres_conn = PostgreSQLConnection(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD)
    postgres_conn.connect()
    try:
        with postgres_conn.conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            cursor.execute(f"CREATE TABLE {table_name} (person1id INT, person2id INT);")
            postgres_conn.conn.commit()

        with postgres_conn.conn.cursor() as cursor:
            with cursor.copy(f"COPY {table_name} (person1id, person2id) FROM STDIN") as copy:
                for edge in g.edges():
                    copy.write_row(edge)
                    copy.write_row((edge[1], edge[0]))
            postgres_conn.conn.commit()

    except Exception as e:
        print(f"An error occurred during PostgreSQL bulk import: {e}")
    finally:
        if postgres_conn:
            postgres_conn.close()


def main(num_nodes: int, avg_friendships: int, neo4j: bool, postgres: bool):
    graph_start_time = time.time()
    g = generate_regular_graph(num_nodes, avg_friendships)
    print(f"Graph generated in {time.time() - graph_start_time:.2f} seconds")
    print(f"Generated a graph with {num_nodes:_} nodes and {len(g.edges()):_} edges")
    export_graph_to_csv(g, neo4j, postgres)
    if neo4j:
        import_graph_to_neo4j()
        print("Graph created in Neo4j database.")

    if postgres:
        bulk_import_to_postgres(g, "Person_knows_Person")
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
