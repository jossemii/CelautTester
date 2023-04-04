import json
import sys
import os
import grpc
from grpcbigbuffer import client as grpcbb

import gateway_pb2
import gateway_pb2_grpc
from main import GATEWAY

import os
import json

ZIP_SOURCE_DIRECTORY = 'src'
SERVICES = '__registry__'
BLOCKS = '__block__'


def generate_service_zip(project_directory: str) -> str:
    # Remove the last character '/' from the path if it exists
    if project_directory[-1] == '/':
        project_directory = project_directory[:-1]

    # Remove the ZIP file and the destination source directory if they already exist
    os.system(f"cd {project_directory}/.service && rm .service.zip && rm -rf {ZIP_SOURCE_DIRECTORY}")

    # Define the complete path for the destination source directory
    complete_source_directory = f"{project_directory}/.service/{ZIP_SOURCE_DIRECTORY}"

    # Create the destination source directory and copy all files and folders from the project there
    os.system(f"mkdir {complete_source_directory}")
    os.system(f'cp -R {project_directory}/* {complete_source_directory}/')

    # Remove the ".service" directory inside the destination source directory
    os.system(f'rm -rf {complete_source_directory}/.service')

    # Read the compilation configuration JSON file
    with open(f'{project_directory}/.service/pre-compile.json', 'r') as config_file:
        compile_config = json.load(config_file)

    # Add a line to the Dockerfile to copy the source files to the working directory
    with open(f'{project_directory}/.service/Dockerfile', 'a') as dockerfile:
        dockerfile.write(f'COPY {ZIP_SOURCE_DIRECTORY} /{compile_config["workdir"]}/')

    # Remove the files and directories specified in the "ignore" list from the configuration
    for file in compile_config['ignore']:
        os.system(f"cd {complete_source_directory} && rm -rf {file}")

    # Add the dependencies
    os.system(f'mkdir {complete_source_directory}/{compile_config["dependencies_directory"]}')
    os.system(f'mkdir {complete_source_directory}/{compile_config["blocks_directory"]}')
    for dependency in compile_config['dependencies']:
        if not os.path.exists(f"{SERVICES}/{dependency}"):
            raise Exception("Dependency not found.")
        os.system(f"cp {SERVICES}/{dependency} {complete_source_directory}/{compile_config['dependencies_directory']}")
        if os.path.isdir(f"{SERVICES}/{dependency}"):
            with open(f"{SERVICES}/{dependency}/_.json", 'r') as dependency_json_file:
                dependency_json = json.load(dependency_json_file)
                for e in dependency_json:
                    if type(e) == list:
                        block: str = e[0]
                        if not os.path.exists(f'{complete_source_directory}/{compile_config["blocks_directory"]}/{block}'):
                            os.system(f"cp {BLOCKS}/{block} {complete_source_directory}/{compile_config['blocks_directory']}")

    # Create a ZIP file of the destination source directory
    os.system(f"cd {project_directory}/.service && zip -r .service.zip .")

    # Remove the destination source directory
    os.system(f"rm -rf {complete_source_directory}")

    # Return the path of the generated ZIP file
    return project_directory + '/.service/.service.zip'


def _compile(partitions_model, partitions_message_mode_parser, repo):
    yield from grpcbb.client_grpc(
        method=gateway_pb2_grpc.GatewayStub(
            grpc.insecure_channel(GATEWAY + ':8090')
        ).Compile,
        input=gateway_pb2.CompileInput(
            partitions_model=partitions_model,
            repo=open(repo, 'rb').read()
        ),
        indices_parser=gateway_pb2.CompileOutput,
        partitions_parser=partitions_model,
        partitions_message_mode_parser=partitions_message_mode_parser
    )


service_zip_dir: str = generate_service_zip(
    project_directory=sys.argv[1]
)

exit()

id: Optional[str] = None
print('Start compile.')
for b in _compile(
        partitions_model=Compile_output_partitions_v1,
        partitions_message_mode_parser=[True, False],
        repo=service_zip_dir
):
    print('b -> ', b)
    if b is gateway_pb2.CompileOutput:
        continue
    elif not id:
        id = b.hex()
    elif id:
        os.system('mv ' + b + ' ' + '__registry__/' + id)
    else:
        raise Exception('\nError with the compiler output.' + str(b))

os.remove(service_zip_dir)
print('service id -> ', id)

print('\n Validate the content.')

validate_id = sha3_256()

for i in grpcbb.read_multiblock_directory('__registry__/' + id + '/'):
    validate_id.update(i)

print('content id (service with meta id)', validate_id.hexdigest())

print('\n Validate the service.')
validate_id = sha3_256()

service_with_meta = gateway_pb2.ServiceWithMeta()
with open('__registry__/' + id + '/wbp.bin', 'rb') as f:
    service_with_meta.ParseFromString(
        f.read()
    )

print('validated service id', validate_id.hexdigest())
