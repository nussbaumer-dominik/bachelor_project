import pandas as pd

# Define the base path and the specific file paths
BASE_PATH = "../data"

file_paths = [
    f'{BASE_PATH}/social-network-sf0.1-merged-fk/Person.csv',
    f'{BASE_PATH}/social-network-sf0.3-merged-fk/Person.csv',
    f'{BASE_PATH}/social-network-sf1-merged-fk/Person.csv'
]

def main():
    # Initialize a list to hold ID sets from each file
    id_sets = []

    for file_path in file_paths:
        df = pd.read_csv(file_path, delimiter='|')
        # Append the set of IDs from this file to the list
        id_sets.append(set(df['id']))

    # Compute the intersection of all ID sets
    common_person_ids = set.intersection(*id_sets)
    common_person_ids = sorted(list(common_person_ids))

    # Print all person IDs that are common across all files
    for person_id in common_person_ids:
        print(person_id)

if __name__ == '__main__':
    main()
