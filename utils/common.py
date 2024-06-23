import datetime
import os
import zipfile
from os import listdir, mkdir, path, remove
from shutil import rmtree


def read_links(filename: str) -> list[list[str]]:
    MAX_BATCH_SIZE: int = 8000
    with open(filename) as f:
        website_links: list = f.readlines()

    link_groups: list[list[str]] = []
    current_group: list[str] = []
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


def get_lines_count_in(file: str) -> int:
    count: int = 0
    try:
        with open(file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    count += 1
    except FileNotFoundError as e:
        print(f"Error: file '{file}' not found: {e}")
        exit(1)

    return count


def archive_results(save_logs=False) -> None:
    """Save results of the analysis to <date-time>.zip archive.

    Keyword arguments:
    save_logs -- add logs folder to archive (optional, default False)
    """
    current_datetime = datetime.datetime.now()
    date_time_str = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")

    archive_filename = f"{date_time_str}.zip"

    if not os.path.exists('results'):
        print("Error: 'results' folder not found.")
        return

    # Create a new ZIP archive
    with zipfile.ZipFile(archive_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk('results'):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, 'results'))

        # Add files from the 'logs' folder to the archive if save_logs is True
        if save_logs and os.path.exists('logs'):
            for root, _, files in os.walk('logs'):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, 'logs'))

    # Move the created archive to the 'results' folder
    if not path.exists('archives'):
        mkdir('archives')
    os.rename(archive_filename, os.path.join('archives', archive_filename))

    print(
        f"Results successfully archived to {os.path.join('results', archive_filename)}")


def clean_logs_directory():
    if path.exists('logs'):
        for content in os.listdir('logs'):
            content_path = path.join('logs', content)
            if path.isfile(content_path):
                remove(content_path)
            else:
                rmtree(content_path, ignore_errors=True)


def clean_results_directory():
    if path.exists('results'):
        for content in listdir('results/'):
            content_path = path.join('results/', content)
            if path.isfile(content_path):
                remove(content_path)
            else:
                rmtree(content_path, ignore_errors=True)
    else:
        mkdir('results')
