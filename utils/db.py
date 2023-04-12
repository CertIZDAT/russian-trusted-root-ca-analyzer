import sqlite3
from os import path, remove

from utils import logger


def create_db_with_name(db_name):
    full_path_to_db = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        logger.logger.info(f'Database with name {db_name} already exists')
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


def write_batch(db_name, timeout, total_ds_size, trusted_ca_count, self_signed_count,
                other_ssl_count, successful_count, unsuccessful_count, error_count,
                path_to_trusted, path_to_self, path_to_other_ssl, path_to_successful,
                path_to_unsuccessful, path_to_request_errors, is_new_dataset=False):

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Read the data from the analysis pipeline
    # Read the contents of the trusted text files into string arrays
    try:
        with open(path_to_trusted, 'r') as trusted_ca:
            trusted_entries = [line.strip() for line in trusted_ca.readlines()]
    except FileNotFoundError:
        logger.logger.warn(f'No such file or directory: {path_to_trusted}')
        trusted_entries = []

    # Read the contents of the self signed text files into string arrays
    try:
        with open(path_to_self, 'r') as self_signed:
            self_entries = [line.strip() for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(f'No such file or directory: {path_to_self}')
        self_entries = []

    # Read the contents of the other ssl error text files into string arrays
    try:
        with open(path_to_other_ssl, 'r') as self_signed:
            other_ssl_entries = [line.strip()
                                 for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(f'No such file or directory: {path_to_other_ssl}')
        other_ssl_entries = []

    # Read the contents of the request errors text files into string arrays
    try:
        with open(path_to_request_errors, 'r') as self_signed:
            request_errors_entries = [line.strip()
                                      for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(
            f'No such file or directory: {path_to_request_errors}')
        request_errors_entries = []

     # Read the contents of the successful request text files into string arrays
    try:
        with open(path_to_successful, 'r') as self_signed:
            successful_entries = [line.strip()
                                  for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(
            f'No such file or directory: {path_to_successful}')
        successful_entries = []

    # Read the contents of the unsuccessful request text files into string arrays
    try:
        with open(path_to_unsuccessful, 'r') as self_signed:
            unsuccessful_entries = [line.strip()
                                    for line in self_signed.readlines()]
    except FileNotFoundError:
        logger.logger.warn(
            f'No such file or directory: {path_to_unsuccessful}')
        unsuccessful_entries = []

    # Convert the string arrays to comma-separated strings
    list_of_trusted_ca_entries_str = ','.join(trusted_entries)
    list_of_self_sign_entries_std = ','.join(self_entries)
    list_of_other_ssl_error_entries_str = ','.join(other_ssl_entries)

    list_of_successful_entries_str = ','.join(successful_entries)
    list_of_unsuccessful_entries_str = ','.join(unsuccessful_entries)
    request_error_entries_str = ','.join(request_errors_entries)

    # Add entries to database
    insert_query = '''
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


def delete_db_with_name(db_name):
    full_path_to_db = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        remove(full_path_to_db)
    else:
        raise __InvalidDataBaseProvided


class __InvalidDataBaseProvided(Exception):
    'Can\'t find database!'
