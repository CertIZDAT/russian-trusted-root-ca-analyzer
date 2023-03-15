from os import path


def count_strings_in_file(file_path):
    full_path = path.abspath(path.expanduser(file_path))
    count = 0
    with open(full_path, 'r') as f:
        for line in f:
            if line.strip():
                count += 1
    print(full_path + ' – count: ' + str(count))
    return count
