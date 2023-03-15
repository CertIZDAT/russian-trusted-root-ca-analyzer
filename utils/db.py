import sqlite3
from os import path, remove
from os.path import abspath, exists, expanduser


def create_db_with_name(db_name):
    full_path_to_db = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        print("Database with name {} already exists".format(db_name))
        return

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Define the schema for the table
    create_table = '''
    CREATE TABLE IF NOT EXISTS statistic_table (
        id INTEGER PRIMARY KEY,
        date_time TEXT NOT NULL,
        trusted_ca_count INTEGER NOT NULL,
        self_signed_count INTEGER NOT NULL,
        list_of_trusted_ca TEXT NOT NULL,
        list_of_self_sign TEXT NOT NULL,
        is_dataset_updated INTEGER NOT NULL
    )
    '''

    cursor.execute(create_table)

    connection.commit()
    connection.close()


def write_batch(db_name, trusted_count, self_count, path_to_trusted, path_to_self, is_new_dataset=False):
    full_path_to_trusted = path.abspath(path.expanduser(path_to_trusted))
    full_path_to_self_sign = path.abspath(path.expanduser(path_to_self))

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Read the contents of the trusted and self text files into string arrays
    with open(full_path_to_trusted, 'r') as trusted_ca, open(full_path_to_self_sign, 'r') as self_signed:
        trusted_entries = [line.strip() for line in trusted_ca.readlines()]
        self_entries = [line.strip() for line in self_signed.readlines()]

    # Convert the string arrays to comma-separated strings
    trusted_entries_str = ','.join(trusted_entries)
    self_entries_str = ','.join(self_entries)

    insert_query = '''
        INSERT INTO statistic_table (date_time, trusted_ca_count, self_signed_count, list_of_trusted_ca, list_of_self_sign, is_dataset_updated)
        VALUES (DATETIME('now'), ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(insert_query, (trusted_count, self_count,
                                      trusted_entries_str, self_entries_str, int(is_new_dataset)))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error executing SQL statement: {e}")
    finally:
        connection.close()


def delete_db_with_name(db_name):
    full_path_to_db = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        remove(full_path_to_db)
    else:
        raise __InvalidDataBaseProvided


class __InvalidDataBaseProvided(Exception):
    "Can't find database!"


def need_to_del_db(need_to_del_db):
    if need_to_del_db:
        full_path_to_db = abspath(expanduser(need_to_del_db))
        if exists(full_path_to_db):
            remove(full_path_to_db)
            print("Database at {} deleted".format(full_path_to_db))
        else:
            print('Can\'t delete database at {}!'.format(full_path_to_db))
            exit(1)
        exit(0)
