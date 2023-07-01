import json
import os
import sys
from hashlib import sha3_256

from typing import Optional, Dict

import grpc
from grpcbigbuffer import client as grpcbb

import gateway_pb2
import gateway_pb2_grpc
from gateway_pb2_grpcbf import Compile_output_partitions_v1
from main import GATEWAY

ZIP_SOURCE_DIRECTORY = 'src'
SERVICES = '__registry__'
BLOCKS = '__block__'


def export_registry(directory: str, compile_config: Dict):
    if compile_config["dependencies_directory"] and compile_config["blocks_directory"]:
        try:
            os.system(f'rm -rf {directory}/{compile_config["dependencies_directory"]}')
        finally:
            os.system(f'mkdir {directory}/{compile_config["dependencies_directory"]}')

        try:
            os.system(f'rm -rf {directory}/{compile_config["blocks_directory"]}')
        finally:
            os.system(f'mkdir {directory}/{compile_config["blocks_directory"]}')

    for dependency in compile_config['dependencies']:
        if not os.path.exists(f"{SERVICES}/{dependency}"):
            raise Exception(f"Dependency not found. {dependency}")
        os.system(f"cp -R {SERVICES}/{dependency} "
                  f"{directory}/{compile_config['dependencies_directory']}")

        if os.path.isdir(f"{SERVICES}/{dependency}"):
            with open(f"{SERVICES}/{dependency}/_.json", 'r') as dependency_json_file:
                dependency_json = json.load(dependency_json_file)
                for e in dependency_json:
                    if type(e) == list:
                        block: str = e[0]
                        if not os.path.exists(
                                f'{directory}/{compile_config["blocks_directory"]}/{block}'
                        ):
                            os.system(f"cp -r {BLOCKS}/{block} "
                                      f"{directory}/{compile_config['blocks_directory']}")


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
    export_registry(directory=complete_source_directory, compile_config=compile_config)

    if compile_config['zip']:
        os.system(f'cd {complete_source_directory} && '
                  f'zip -r services.zip '
                  f'{compile_config["dependencies_directory"]} {compile_config["blocks_directory"]}')
        os.system(f'cd {complete_source_directory} && '
                  f'rm -rf {compile_config["dependencies_directory"]} {compile_config["blocks_directory"]}')

    # Create a ZIP file of the destination source directory
    os.system(f"cd {project_directory}/.service && zip -r .service.zip .")

    # Delete the last line to the Dockerfile to copy the source files to the working directory
    os.system('sed -i "$ d" {0}'.format(f"{project_directory}/.service/Dockerfile"))

    # Remove the destination source directory
    os.system(f"rm -rf {complete_source_directory}")

    # Return the path of the generated ZIP file
    return project_directory + '/.service/.service.zip'


def _compile(partitions_model, partitions_message_mode_parser, repo, node: str):
    yield from grpcbb.client_grpc(
        method=gateway_pb2_grpc.GatewayStub(
            grpc.insecure_channel(node + ':8090')
        ).Compile,
        input=gateway_pb2.CompileInput(
            partitions_model=partitions_model,
            repo=open(repo, 'rb').read()
        ),
        indices_parser=gateway_pb2.CompileOutput,
        partitions_parser=partitions_model,
        partitions_message_mode_parser=partitions_message_mode_parser
    )


if __name__ == '__main__':
    if not os.path.exists('__cache__'):
        os.mkdir('__cache__')

    if not os.path.exists('__registry__'):
        os.mkdir('__registry__')

    service_zip_dir: str = generate_service_zip(
        project_directory=sys.argv[1]
    )

    id: Optional[str] = None
    print('Start compile.')
    for b in _compile(
            partitions_model=Compile_output_partitions_v1,
            partitions_message_mode_parser=[True, False],
            repo=service_zip_dir,
            node=GATEWAY if len(sys.argv) == 2 else sys.argv[2]
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

    try:
        for i in grpcbb.read_multiblock_directory('__registry__/' + id + '/'):
            validate_id.update(i)
    except Exception as e:
        print(f"¿Tal vez no tiene bloques? {str(e)}")

    print('content id (service with meta id)', validate_id.hexdigest())
