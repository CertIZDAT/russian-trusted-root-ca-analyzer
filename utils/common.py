def read_links(filename: str) -> list[list[str]]:
    MAX_BATCH_SIZE: int = 8000
    with open(filename, 'r') as f:
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
