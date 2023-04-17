SORTER = ''
RANDOM = '545d3cbdbfc389352259512383c85db7f69787f1a4d5743018cc9bec86a2bda1'
REGRESION = '84d568bb073fdd20e49109699a0211189a66dc16f3381759f97add320d497123'
WALL = ''
WALK = ''
FRONTIER = 'b9032bd1196fbcbcc3cc676e9e04c7ebff77952554e2b9e37e8ae630eba49f66'

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
