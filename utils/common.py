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


def read_entries_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f'No such file or directory: {file_path}')
        return []
