import sys

# Check if the correct number of arguments were provided
if len(sys.argv) != 3:
    print('Usage: python deduplicate.py input_file output_file')
    sys.exit()

# Get the input and output file names from the command line arguments
input_file_name: str = sys.argv[1]
output_file_name: str = sys.argv[2]

# Open the input file for reading
with open(input_file_name) as input_file:
    # Read the contents of the input file into a list
    links: list[str] = input_file.readlines()

# Use a set to remove duplicates from the list of links
unique_links: set[str] = set(links)

# Open the output file for writing
with open(output_file_name, 'w') as output_file:
    # Write the unique links to the output file, one per line
    for link in unique_links:
        output_file.write(link)

print(
    f'Deduplication of the {input_file_name} completed successfully')
