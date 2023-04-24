import sqlite3
from os import path, remove
from sqlite3 import Connection, Cursor

from utils import logger


# TODO: Read db_name from global
def create_db_with_name(db_name: str) -> None:
    full_path_to_db: str = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        logger.logger.info(f'Database with name {db_name} already exists')
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
        trusted_ca_count INTEGER NOT NULL,
        self_signed_count INTEGER NOT NULL,
        other_ssl_count INTEGER NOT NULL,
        successful_count INTEGER NOT NULL,
        unsuccessful_count INTEGER NOT NULL,
        error_count INTEGER NOT NULL,
        list_of_trusted_ca TEXT NOT NULL,
        list_of_self_sign TEXT NOT NULL,
        list_of_other_ssl_error TEXT NOT NULL,
        list_of_successful TEXT NOT NULL,
        list_of_unsuccessful TEXT NOT NULL,
        list_of_request_error TEXT NOT NULL,
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


def write_batch(db_name: str, timeout: int, total_ds_size: int, trusted_ca_count: int, self_signed_count: int,
                other_ssl_count: int, successful_count: int, unsuccessful_count: int, error_count: int,
                path_to_trusted: str, path_to_self: str, path_to_other_ssl: str, path_to_successful: str,
                path_to_unsuccessful: str, path_to_request_errors: str, is_new_dataset: bool = False) -> None:
    connection: Connection = sqlite3.connect(db_name)
    cursor: Cursor = connection.cursor()

    # Read the data from the analysis pipeline
    # Read the contents of the trusted text files into string arrays
    try:
        with open(path_to_trusted, 'r') as trusted_ca:
            trusted_entries = [line.strip() for line in trusted_ca.readlines()]
    except FileNotFoundError:
        logger.logger.warn(f'No such file or directory: {path_to_trusted}')
        trusted_entries: list[str] = []

    # Read the contents of the self-signed text files into string arrays
    try:
        with open(path_to_self, 'r') as self_signed:
            self_entries: list[str] = [line.strip() for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(f'No such file or directory: {path_to_self}')
        self_entries: list[None] = []

    # Read the contents of the other ssl error text files into string arrays
    try:
        with open(path_to_other_ssl, 'r') as self_signed:
            other_ssl_entries: list[str] = [line.strip()
                                            for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(f'No such file or directory: {path_to_other_ssl}')
        other_ssl_entries: list[None] = []

    # Read the contents of the request errors text files into string arrays
    try:
        with open(path_to_request_errors, 'r') as self_signed:
            request_errors_entries: list[str] = [line.strip()
                                                 for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(
            f'No such file or directory: {path_to_request_errors}')
        request_errors_entries: list[None] = []

    # Read the contents of the successful request text files into string arrays
    try:
        with open(path_to_successful, 'r') as self_signed:
            successful_entries: list[str] = [line.strip()
                                             for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(
            f'No such file or directory: {path_to_successful}')
        successful_entries: list[None] = []

    # Read the contents of the unsuccessful request text files into string arrays
    try:
        with open(path_to_unsuccessful, 'r') as self_signed:
            unsuccessful_entries: list[str] = [line.strip()
                                               for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(
            f'No such file or directory: {path_to_unsuccessful}')
        unsuccessful_entries: list[None] = []

    # Convert the string arrays to comma-separated strings
    list_of_trusted_ca_entries_str: str = ','.join(trusted_entries)
    list_of_self_sign_entries_std: str = ','.join(self_entries)
    list_of_other_ssl_error_entries_str: str = ','.join(other_ssl_entries)

    list_of_successful_entries_str: str = ','.join(successful_entries)
    list_of_unsuccessful_entries_str: str = ','.join(unsuccessful_entries)
    request_error_entries_str: str = ','.join(request_errors_entries)

    # Add entries to database
    insert_query: str = '''
        INSERT INTO statistic_table (date_time, timeout, total_ds_size, trusted_ca_count, 
        self_signed_count, other_ssl_count, successful_count, unsuccessful_count, 
        error_count, list_of_trusted_ca, list_of_self_sign, list_of_other_ssl_error, 
        list_of_successful, list_of_unsuccessful, list_of_request_error, is_dataset_updated)
        VALUES (DATETIME('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(insert_query, (timeout,
                                      total_ds_size,
                                      trusted_ca_count,
                                      self_signed_count,
                                      other_ssl_count,
                                      successful_count,
                                      unsuccessful_count,
                                      error_count,
                                      list_of_trusted_ca_entries_str,
                                      list_of_self_sign_entries_std,
                                      list_of_other_ssl_error_entries_str,
                                      list_of_successful_entries_str,
                                      list_of_unsuccessful_entries_str,
                                      request_error_entries_str,
                                      int(is_new_dataset == 'True' or is_new_dataset == 'true')))
        connection.commit()
    except sqlite3.Error as e:
        logger.logger.error(f'Error executing SQL statement: {e}')
        connection.close()
        exit(1)
    finally:
        connection.close()
