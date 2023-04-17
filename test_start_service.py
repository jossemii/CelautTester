# Test combine method.
import celaut_pb2
import gateway_pb2_grpcbf, gateway_pb2, gateway_pb2_grpc
import grpc
import grpcbigbuffer
from grpcbigbuffer.client import Dir, client_grpc
from main import GATEWAY, REGRESION, RANDOM, SHA3_256


def service_extended():
    # Send partition model.
    yield gateway_pb2.Client(client_id='dev')
    print(1)
    yield gateway_pb2.HashWithConfig(
        hash=celaut_pb2.Any.Metadata.HashTag.Hash(
            type=bytes.fromhex(SHA3_256),
            value=bytes.fromhex(REGRESION)
        ),
        config=celaut_pb2.Configuration(),
        min_sysreq=celaut_pb2.Sysresources(
            mem_limit=50 * pow(10, 6)
        )
    )
    print(2)
    yield (
         gateway_pb2.ServiceWithMeta,
        Dir('__registry__/' + REGRESION)
    )
    print(3)


g_stub = gateway_pb2_grpc.GatewayStub(
    grpc.insecure_channel(GATEWAY + ':8090'),
)

random = next(client_grpc(
    method=g_stub.StartService,
    input=service_extended(),
    indices_parser=gateway_pb2.Instance,
    partitions_message_mode_parser=True,
    indices_serializer=gateway_pb2_grpcbf.StartService_input
))
print(f'random partition -> {random}')
