# Test combine method.

import gateway_pb2_grpcbf, gateway_pb2, gateway_pb2_grpc
import grpc
import grpcbigbuffer
from grpcbigbuffer.client import Dir, client_grpc
from main import GATEWAY

def service_extended():

    # Send partition model.
    yield ( 
        gateway_pb2.ServiceWithMeta,
        Dir('__registry__/cda02e6e193b0c39e330212f14a119c4b91b0b64d7d228a76918d9d84c2105fb')
    )    

g_stub = gateway_pb2_grpc.GatewayStub(
    grpc.insecure_channel(GATEWAY+':8090'),
)

random = next(client_grpc(
    method = g_stub.StartService,
    input = service_extended(),
    indices_parser = gateway_pb2.Instance,
    partitions_message_mode_parser = True,
    indices_serializer = gateway_pb2_grpcbf.StartService_input,
    partitions_serializer = gateway_pb2_grpcbf.StartService_input_partitions_v1
))