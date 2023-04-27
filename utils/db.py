import sqlite3
from os import path
from sqlite3 import Connection, Cursor

from utils.logger import logger


def create_db_with_name(db_name: str) -> None:
    full_path_to_db: str = path.abspath(path.expanduser(db_name))
    if path.exists(full_path_to_db):
        return

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Define the schema for the table
    create_table: str = '''
    CREATE TABLE IF NOT EXISTS statistic_table (
        id INTEGER PRIMARY KEY,
        date_time TEXT NOT NULL,
        timeout INTEGER NOT NULL,
        gov_ca_list TEXT NOT NULL,
        gov_ss_list TEXT NOT NULL,
        gov_other_ssl_err_list TEXT NOT NULL,
        social_ca_list TEXT NOT NULL,
        social_ss_list TEXT NOT NULL,
        social_other_ssl_err_list TEXT NOT NULL,    
        top_ca_list TEXT NOT NULL,
        top_ss_list TEXT NOT NULL,
        top_other_ssl_err TEXT NOT NULL,
        is_dataset_updated INTEGER NOT NULL
    )
    '''

    try:
        cursor.execute(create_table)
    except sqlite3.Error as e:
        logger.error(
            f'Error can\'t execute SQL query for table creation: {e}')
        connection.close()
        exit(1)

    try:
        connection.commit()
    except sqlite3.Error as e:
        logger.error(
            f'Error can\'t execute SQL query for table creation: {e}')
        connection.close()
        exit(1)
    finally:
        connection.close()


def save_res_to_db(db_name: str,
                   timeout: int,
                   is_new_dataset: bool = False) -> None:
    connection: Connection = sqlite3.connect(db_name)
    cursor: Cursor = connection.cursor()

    res_folder: str = 'results'
    ca_file: str = 'russian_trusted_ca.txt'
    self_sign_file: str = 'ru_self_sign.txt'
    other_ssl_err_file: str = 'other_ssl_err.txt'

    categories: list[str] = ['government', 'social', 'top']
    entries: list = [[] for _ in range(3)]

    for i, category in enumerate(categories):
        ca_path: str = path.join(res_folder, category, ca_file)
        ss_path: str = path.join(res_folder, category, self_sign_file)
        ssl_path: str = path.join(res_folder, category, other_ssl_err_file)

        entries[i] = (_read_entries(ca_path), _read_entries(ss_path), _read_entries(ssl_path))

    gov_ca_entries = ','.join(entries[0][0])
    gov_ss_entries = ','.join(entries[0][1])
    gov_ssl_entries = ','.join(entries[0][2])

    social_ca_entries = ','.join(entries[1][0])
    social_ss_entries = ','.join(entries[1][1])
    social_ssl_entries = ','.join(entries[1][2])

    top_ca_entries = ','.join(entries[2][0])
    top_ss_entries = ','.join(entries[2][1])
    top_ssl_entries = ','.join(entries[2][2])

    # Add entries to database
    insert_query: str = '''
        INSERT INTO statistic_table (date_time, timeout, 
        gov_ca_list, gov_ss_list, gov_other_ssl_err_list,
        social_ca_list, social_ss_list, social_other_ssl_err_list, 
        top_ca_list, top_ss_list, top_other_ssl_err, 
        is_dataset_updated)
        VALUES (DATETIME('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        cursor.execute(insert_query, (timeout,
                                      gov_ca_entries, gov_ss_entries, gov_ssl_entries,
                                      social_ca_entries, social_ss_entries, social_ssl_entries,
                                      top_ca_entries, top_ss_entries, top_ssl_entries,
                                      int(is_new_dataset == 'True' or is_new_dataset == 'true')))
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f'Error executing SQL statement: {e}')
        connection.close()
        exit(1)
    finally:
        connection.close()


def _read_entries(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        logger.warning(f'No such file or directory: {file_path}')
        return []
