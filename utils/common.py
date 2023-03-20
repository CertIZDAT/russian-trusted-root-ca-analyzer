from os import path, remove

from utils import logger


def count_strings_in_file(file_path):
    try:
        full_path = path.abspath(path.expanduser(file_path))
        count = 0
        with open(full_path, 'r') as f:
            for line in f:
                if line.strip() and not line == '\n':
                    count += 1
        logger.logger.info(f'{full_path} – total lines: {str(count)}')
        return count
    except FileNotFoundError as e:
        logger.logger.error(f'No such file or directory: {full_path}')
        return 0


def delete_old_res():
    # Remove output files from previous runs
    files_to_delete = [
        'successful.txt',
        'unsuccessful.txt',
        'ssl_cert_err.txt',
        'request_errors.txt',
        'other_ssl_cert_err.txt',
        'ssl_self_sign_err.txt'
    ]
    for file in files_to_delete:
        if path.exists(file):
            remove(file)


def read_links(filename):
    max_batch_size = 8000
    with open(filename, 'r') as f:
        website_links = f.readlines()

    link_groups = []
    current_group = []
    for link in website_links:
        current_group.append(link.strip())
        if len(current_group) == max_batch_size:
            link_groups.append(current_group)
            current_group = []

    if current_group:
        link_groups.append(current_group)

    return link_groups
