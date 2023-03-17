from os import path, remove


def count_strings_in_file(file_path):
    try:
        full_path = path.abspath(path.expanduser(file_path))
        count = 0
        with open(full_path, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1
        print(f'{full_path} – total lines: {str(count)}')
        return count
    except FileNotFoundError as e:
        print(f'No such file or directory: {full_path}')
        return 0


def delete_old_res():
    # remove output files from previous runs
    if path.exists('successful.txt'):
        remove('successful.txt')
    if path.exists('unsuccessful.txt'):
        remove('unsuccessful.txt')
    if path.exists('ssl_cert_err.txt'):
        remove('ssl_cert_err.txt')
    if path.exists('request_errors.txt'):
        remove('request_errors.txt')
    if path.exists('other_ssl_cert_err.txt'):
        remove('other_ssl_cert_err.txt')
    if path.exists('ssl_self_sign_err.txt'):
        remove('ssl_self_sign_err.txt')


def read_entries_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {file_path}')
        return []
