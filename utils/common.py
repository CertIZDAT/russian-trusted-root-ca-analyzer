from os import path

from utils import logger


def count_strings_in_file(file_path):
    if not path.exists(file_path):
        logger.logger.error(f'No such file or directory: {file_path}')
        return 0
    try:
        full_path = path.abspath(path.expanduser(file_path))
        count = 0
        with open(full_path, 'r') as f:
            for line in f:
                if line.strip() and not line == '\n' and not line.startswith('#'):
                    count += 1
        return count
    except FileNotFoundError as e:
        logger.logger.error(f'No such file or directory: {full_path}')
        return 0


def read_links(filename):
    MAX_BATCH_SIZE = 8000
    with open(filename, 'r') as f:
        website_links = f.readlines()

    link_groups = []
    current_group = []
    for link in website_links:
        if link.startswith('#'):
            continue
        current_group.append(link.strip())
        if len(current_group) == MAX_BATCH_SIZE:
            link_groups.append(current_group)
            current_group = []

    if current_group:
        link_groups.append(current_group)

    return link_groups
