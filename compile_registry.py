import json
import os
import sys

from compile import export_registry

ZIP_SOURCE_DIRECTORY = 'src'
SERVICES = '__registry__'
BLOCKS = '__block__'


project_directory: str = sys.argv[1]
# Remove the last character '/' from the path if it exists
if project_directory[-1] == '/':
    project_directory = project_directory[:-1]

# Remove the ZIP file and the destination source directory if they already exist
os.system(f"cd {project_directory}/.service && rm .service.zip && rm -rf {ZIP_SOURCE_DIRECTORY}")

# Read the compilation configuration JSON file
with open(f'{project_directory}/.service/pre-compile.json', 'r') as config_file:
    compile_config = json.load(config_file)

# Add the dependencies
export_registry(directory=project_directory, compile_config=compile_config)
