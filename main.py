SORTER = 'fe0f2ac0ba19e71ffcb02bafca8e4c4479ee11092d161d8ba83126f8a1dcfc4f'
RANDOM = '19a829e198c47c06fb9641625590b08a0a5729f073250735f5f48d335e3c74bb'
REGRESION = '73e886ef1ab3f241600f10ca8f1f7cfe7d3b31382f1a414d187f7c5a0d35166a'
WALL = 'e19c12d159b6d3bbce73006d23a2f0604e3e4d6510ae1c4e8d4c595dc6455c43'
WALK = '1bca76d3cbddf4eb2e81acb84dd2aa0bd76dc38affc088c4ae9722529cacae99'
FRONTIER = '35dc7bb30403e3e02410eb1cc9fd7be10d470f0b908dc2f7fc3829c84d31dbff'

LISIADO_UNDER = ''
LISIADO_OVER = ''

SHA3_256 = 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'

WHISKY = ''
MOJITO = '192.168.1.16'
TEQUILA = '192.168.1.65'
LOCALHOST = 'localhost'
CODESPACE = 'jossemii-hypernode-xqvwggjxhr5w-8090.githubpreview.dev'
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
