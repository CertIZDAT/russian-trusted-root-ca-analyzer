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
