import sqlite3
from os import path
from sqlite3 import Connection, Cursor

from utils import logger


# TODO: Read db_name from global
def create_db_with_name(db_name: str) -> None:
    full_path_to_db: str = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        return

    connection: Connection = sqlite3.connect(db_name)
    cursor: Cursor = connection.cursor()

    # Define the schema for the table
    create_table: str = '''
    CREATE TABLE IF NOT EXISTS statistic_table (
        id INTEGER PRIMARY KEY,
        date_time TEXT NOT NULL,
        timeout INTEGER NOT NULL,
        total_ds_size INTEGER NOT NULL,
        list_of_trusted_ca TEXT NOT NULL,
        list_of_self_sign TEXT NOT NULL,
        list_of_other_ssl_error TEXT NOT NULL,
        is_dataset_updated INTEGER NOT NULL
    )
    '''

    try:
        cursor.execute(create_table)
    except sqlite3.Error as e:
        logger.logger.error(
            f'Error can\'t execute SQL query for table creation: {e}')
        connection.close()
        exit(1)

    try:
        connection.commit()
    except sqlite3.Error as e:
        logger.logger.error(
            f'Error can\'t execute SQL query for table creation: {e}')
        connection.close()
        exit(1)
    finally:
        connection.close()


def save_res_to_db(db_name: str,
                   timeout: int,
                   total_ds_size: int,
                   trusted_ca_path: str,
                   self_sign_path: str,
                   other_ssl_err_path: str,
                   is_new_dataset: bool = False) -> None:
    connection: Connection = sqlite3.connect(db_name)
    cursor: Cursor = connection.cursor()

    # Read the data from the analysis pipeline
    # Read the contents of the trusted text files into string arrays
    try:
        with open(trusted_ca_path, 'r') as trusted_ca:
            trusted_entries = [line.strip() for line in trusted_ca.readlines()]
    except FileNotFoundError:
        logger.logger.warning(f'No such file or directory: {trusted_ca_path}')
        trusted_entries: list[str] = []

    # Read the contents of the self-signed text files into string arrays
    try:
        with open(self_sign_path, 'r') as self_signed:
            self_entries: list[str] = [line.strip() for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warning(f'No such file or directory: {self_sign_path}')
        self_entries: list[None] = []

    # Read the contents of the other ssl error text files into string arrays
    try:
        with open(other_ssl_err_path, 'r') as self_signed:
            other_ssl_entries: list[str] = [line.strip()
                                            for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warning(f'No such file or directory: {other_ssl_err_path}')
        other_ssl_entries: list[None] = []

    # Convert the string arrays to comma-separated strings
    list_of_trusted_ca_entries: str = ','.join(trusted_entries)
    list_of_self_sign_entries: str = ','.join(self_entries)
    list_of_other_ssl_error_entries: str = ','.join(other_ssl_entries)

    # Add entries to database
    insert_query: str = '''
        INSERT INTO statistic_table (date_time, timeout, total_ds_size, list_of_trusted_ca, 
        list_of_self_sign, list_of_other_ssl_error, is_dataset_updated)
        VALUES (DATETIME('now'), ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(insert_query, (timeout,
                                      total_ds_size,
                                      list_of_trusted_ca_entries,
                                      list_of_self_sign_entries,
                                      list_of_other_ssl_error_entries,
                                      int(is_new_dataset == 'True' or is_new_dataset == 'true')))
        connection.commit()
    except sqlite3.Error as e:
        logger.logger.error(f'Error executing SQL statement: {e}')
        connection.close()
        exit(1)
    finally:
        connection.close()
