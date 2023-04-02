import buffer_pb2
from gateway_pb2_grpcbf import Compile_output_partitions_v1
import gateway_pb2_grpc, grpc, gateway_pb2, sys, os
from grpcbigbuffer import client as grpcbigbuffer
from grpcbigbuffer.block_driver import generate_wbp_file

from main import GATEWAY


def compile(partitions_model, partitions_message_mode_parser, repo):
    for b in grpcbigbuffer.client_grpc(
        method = gateway_pb2_grpc.GatewayStub(
                    grpc.insecure_channel(GATEWAY+':8090')
                ).Compile,
        input = gateway_pb2.CompileInput(  # Sería mas eficiente si se envia particionado Dir(.service.zip) y partitions_model.
                    partitions_model = partitions_model,
                    repo = open(repo, 'rb').read()
                ),
        indices_parser = gateway_pb2.CompileOutput,
        partitions_parser = partitions_model,
        partitions_message_mode_parser = partitions_message_mode_parser
    ): yield b

id = None
print('Start compile.')
for b in compile(
    partitions_model =  Compile_output_partitions_v1,
    partitions_message_mode_parser = [True, False],
    repo = '.service.zip'
): 
    print('b -> ', b)
    if b is gateway_pb2.CompileOutput: continue
    elif not id: 
        id = b.hex()
    elif id: 
        os.system('mv '+b+' '+'__registry__/'+id)
    else: 
        raise Exception('\nError with the compiler output.'+ str(b))
    

print('service id -> ', id)

print('\n Validate the content.')
from hashlib import sha3_256
validate_id = sha3_256()

for i in grpcbigbuffer.read_multiblock_directory('__registry__/'+id+'/'):
    validate_id.update(i)

print('content id (service with meta id)', validate_id.hexdigest())

print('\n Validate the service.')
validate_id = sha3_256()

service_with_meta = gateway_pb2.ServiceWithMeta()
with open('__registry__/'+id+'/wbp.bin', 'rb') as f:
    service_with_meta.ParseFromString(
        f.read()
    )

print('validated service id', validate_id.hexdigest())