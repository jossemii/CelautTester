SORTER = 'f03a32ebdc258a2bd3f59a01527a44bfe7dff68e86b57daa944a7e6cac6c61ae'
RANDOM = 'cdb42c2fa50f3374e7d324a4b91e003a238ab39a8fd57c08d4e33da8359218c7'
REGRESION = '754c007d275fd65ad41af042defcd3eb52bc50e42590d4135978664826f8e382'
WALL = ''
WALK = ''
FRONTIER = 'd1cb88ec9658cdbdaa169b2e56b0efe85f5cdd585e20a848e78e25bbf29062cf'

LISIADO_UNDER = ''
LISIADO_OVER = ''

SHA3_256 = 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'

MOJITO = '192.168.1.14'
WHISKY = '192.168.1.65'
LOCALHOST = 'localhost'
GATEWAY = WHISKY

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
