import sqlite3
from os import path, remove
from os.path import abspath, exists, expanduser


def create_db_with_name(db_name):
    full_path_to_db = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        print(f'Database with name {db_name} already exists')
        return

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Define the schema for the table
    create_table = '''
    CREATE TABLE IF NOT EXISTS statistic_table (
        id INTEGER PRIMARY KEY,
        date_time TEXT NOT NULL,
        timeout INTEGER NOT NULL,
        total_ds_size INTEGER NOT NULL,
        trusted_ca_count INTEGER NOT NULL,
        self_signed_count INTEGER NOT NULL,
        list_of_trusted_ca TEXT NOT NULL,
        list_of_self_sign TEXT NOT NULL,
        list_of_request_error TEXT NOT NULL,
        list_of_successful TEXT NOT NULL,
        list_of_unsuccessful TEXT NOT NULL,
        is_dataset_updated INTEGER NOT NULL
    )
    '''

    cursor.execute(create_table)

    connection.commit()
    connection.close


def write_batch(db_name, timeout, total_ds_size, trusted_count, self_count,
                path_to_trusted, path_to_self, list_of_request_error,
                list_of_successful, list_of_unsuccessful, is_new_dataset=False):

    full_path_to_trusted = path.abspath(path.expanduser(path_to_trusted))
    full_path_to_self_sign = path.abspath(path.expanduser(path_to_self))

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Read the contents of the trusted text files into string arrays
    try:
        with open(full_path_to_trusted, 'r') as trusted_ca:
            trusted_entries = [line.strip() for line in trusted_ca.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {full_path_to_trusted}')
        trusted_entries = []

    # Read the contents of the self signed text files into string arrays
    try:
        with open(full_path_to_self_sign, 'r') as self_signed:
            self_entries = [line.strip() for line in self_signed.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {full_path_to_self_sign}')
        self_entries = []

    # Read the contents of the request errors text files into string arrays
    try:
        with open(list_of_request_error, 'r') as self_signed:
            request_errors_entries = [line.strip()
                                      for line in self_signed.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {list_of_request_error}')
        request_errors_entries = []

    # Read the contents of the successful request text files into string arrays
    try:
        with open(list_of_successful, 'r') as self_signed:
            successful_entries = [line.strip()
                                  for line in self_signed.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {list_of_successful}')
        successful_entries = []

    # Read the contents of the unsuccessful request text files into string arrays
    try:
        with open(list_of_unsuccessful, 'r') as self_signed:
            unsuccessful_entries = [line.strip()
                                    for line in self_signed.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {list_of_unsuccessful}')
        unsuccessful_entries = []

    # Convert the string arrays to comma-separated strings
    trusted_entries_str = ','.join(trusted_entries)
    self_entries_str = ','.join(self_entries)
    request_error_entries_str = ','.join(request_errors_entries)
    list_of_successful_entries_str = ','.join(successful_entries)
    list_of_unsuccessful_entries_str = ','.join(unsuccessful_entries)

    insert_query = '''
        INSERT INTO statistic_table (date_time, timeout, total_ds_size, trusted_ca_count, 
        self_signed_count, list_of_trusted_ca, list_of_self_sign, list_of_request_error, 
        list_of_successful, list_of_unsuccessful, is_dataset_updated)
        VALUES (DATETIME('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(insert_query, (timeout, total_ds_size, trusted_count, self_count,
                                      trusted_entries_str, self_entries_str, request_error_entries_str,
                                      list_of_successful_entries_str, list_of_unsuccessful_entries_str,
                                      int(is_new_dataset == 'True')))
        connection.commit()
    except sqlite3.Error as e:
        print(f'Error executing SQL statement: {e}')
        connection.close()
        exit(1)
    finally:
        connection.close()


def delete_db_with_name(db_name):
    full_path_to_db = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        remove(full_path_to_db)
    else:
        raise __InvalidDataBaseProvided


class __InvalidDataBaseProvided(Exception):
    'Can\'t find database!'


def need_to_del_db(need_to_del_db):
    '''This function deletes the database with the specified name. After deletion, this function sends an exit code of 0 or 1.'''
    if need_to_del_db:
        full_path_to_db = abspath(expanduser(need_to_del_db))
        if exists(full_path_to_db):
            remove(full_path_to_db)
            print(f'Database at {full_path_to_db} deleted')
        else:
            print(f'Can\'t delete database at {full_path_to_db}!')
            exit(1)
        exit(0)
