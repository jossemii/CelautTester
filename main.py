SORTER = '3b094c06888f70217d4b0506cbb254841d8728c6c8fa0e28cc5b3ad96fe66aa2'
RANDOM = '5ee9fde07f08bb3c7683761eeb602bc25bb1019bda7e9ea4cb32fecae7de3d05'
REGRESION = '6fa3905700851f8a43030c01d626bde3c9c46e23671d8e105e201371094d8d55'
WALL = ''
WALK = ''
FRONTIER = 'f2eab4154128df07d5eee279a88e40c8336cc6a396883d9e35ed71a481118623'

LISIADO_UNDER = ''
LISIADO_OVER = ''

SHA3_256 = 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'

WHISKY = ''
MOJITO = '192.168.1.16'
TEQUILA = '192.168.1.65'
LOCALHOST = 'localhost'
GATEWAY = TEQUILA

import celaut_pb2, gateway_pb2
from grpcbigbuffer.client import Dir


def to_gas_amount(gas_amount: int) -> gateway_pb2.GasAmount:
    return gateway_pb2.GasAmount(n=str(gas_amount))


def from_gas_amount(gas_amount: gateway_pb2.GasAmount) -> int:
    i: int = str(gas_amount.gas_amount)[::-1].find('.')
    return int(gas_amount.gas_amount * pow(10, i) * pow(10, gas_amount.exponent - i))


def generator(_hash: str, mem_limit: int = 50 * pow(10, 6)):
    try:
        yield gateway_pb2.Client(client_id='dev')
        yield gateway_pb2.HashWithConfig(
            hash=celaut_pb2.Any.Metadata.HashTag.Hash(
                type=bytes.fromhex(SHA3_256),
                value=bytes.fromhex(_hash)
            ),
            config=celaut_pb2.Configuration(),
            min_sysreq=celaut_pb2.Sysresources(
                mem_limit=mem_limit
            )
        )
    except Exception as e:
        print(e)

    # Send partition model.
    yield (
        gateway_pb2.ServiceWithMeta,
        Dir('__registry__/' + _hash)
    )


def service_extended(hash):
    for t in generator(_hash=hash): yield t
