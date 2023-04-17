from genericpath import isfile
from gateway_pb2_grpcbf import StartService_input
import grpc, gateway_pb2, gateway_pb2_grpc, api_pb2, api_pb2_grpc, threading, solvers_dataset_pb2
from time import sleep, time

from main import GATEWAY, RANDOM, FRONTIER, WALL, WALK, service_extended
from grpcbigbuffer.client import Dir, client_grpc



g_stub = gateway_pb2_grpc.GatewayStub(
    grpc.insecure_channel(GATEWAY + ':8090'),
)

print('Get new services....')

c_stub = api_pb2_grpc.SolverStub(
    grpc.insecure_channel('localhost:8081')
    )

print('Tenemos clasificador. ', c_stub)
try:
    dataset = solvers_dataset_pb2.DataSet()
    dataset.ParseFromString(open('dataset.bin', 'rb').read())
    next(client_grpc(
        method=c_stub.AddDataSet,
        input=dataset,
    ))
    print('Dataset añadido.') 
except Exception as e:
    print('No tenemos dataset.', str(e))
    pass

print('Subiendo solvers al clasificador.')
# Añade solvers.
for s in [FRONTIER]:
    print('     ', s, isfile('__registry__/'+s))
    next(client_grpc(
        method = c_stub.UploadSolver,
        input = (gateway_pb2.ServiceWithMeta, Dir('__registry__/'+s))
    ))

print('tenemos el solver.')
# Get random cnf
random_cnf_service = next(client_grpc(
    method = g_stub.StartService,
    indices_parser = gateway_pb2.Instance,
    input = service_extended(hash = RANDOM),
    indices_serializer = StartService_input,
    partitions_message_mode_parser = True
))

print(random_cnf_service)
uri=random_cnf_service.instance.uri_slot[0].uri[0]
r_uri = uri.ip +':'+ str(uri.port)
r_stub = api_pb2_grpc.RandomStub(
    grpc.insecure_channel(r_uri)
    )

print('Tenemos random. ', r_stub)

if True:  #if input("\nGo to train? (y/n)")=='y':
    print('Iniciando entrenamiento...')
    
    # Inicia el entrenamiento.
    next(client_grpc(
        method=c_stub.StartTrain
    ))

    print('Wait to train the model ...')
    for i in range(5):
        for j in range(60):
            print(' time ', i, j)
            sleep(60)
        
        print('Obtiene el data_set.')
        try:
            dataset = next(client_grpc(
                method=c_stub.GetDataSet,
                indices_parser=api_pb2.solvers__dataset__pb2.DataSet,
                partitions_message_mode_parser=True
            ))
            with open('dataset.bin', 'wb') as f:
                f.write(dataset.SerializeToString())
        except Exception as e:
            print('Error getting dataset -> ', e)

        cnf = next(client_grpc(
            method = r_stub.RandomCnf,
            indices_parser = api_pb2.Cnf,
            partitions_message_mode_parser = True
        ))
        print('cnf -> ', cnf)
        # Comprueba si sabe generar una interpretacion (sin tener ni idea de que tal
        # ha hecho la seleccion del solver.)
        print('\n ---- ', i)
        print(' SOLVING CNF ...')
        t = time()
        interpretation = next(client_grpc(
            method=c_stub.Solve,
            indices_parser={1: api_pb2.Interpretation, 2: api_pb2.Empty},
            partitions_message_mode_parser={1: True, 2: False},
            input=cnf,
            indices_serializer=api_pb2.Cnf
        ))
        print(interpretation, str(time()-t)+' OKAY THE INTERPRETATION WAS ') if type(interpretation) != str else print('Tensor is not ready yet.')

    sleep(60)

print('Termina el entrenamiento')
# En caso de que estubiera entrenando lo finaliza.
try:
    next(client_grpc(
        method=c_stub.StopTrain
    ))
except Exception as e:
    print('e -> ', e)
    raise e
print('Entrenamiento terminado')

# Comprueba si sabe generar una interpretacion (sin tener ni idea de que tal
# ha hecho la seleccion del solver.)
def final_test(c_stub, r_stub, i, j):
    cnf = next(client_grpc(
        method=r_stub.RandomCnf,
        indices_parser=api_pb2.Cnf,
        partitions_message_mode_parser=True
    ))
    t = time()
    try:
        interpretation = next(client_grpc(
            method=c_stub.Solve,
            input=cnf,
            indices_parser=api_pb2.Interpretation,
            partitions_message_mode_parser=True
        ))
    except Exception as e:
        print(i, j, '  e -> ', e)
    print(interpretation, str(time()-t)+'THE FINAL INTERPRETATION IN THREAD '+str(threading.get_ident()),' last time ', i, j)


for i in range(1):
    sleep(10)
    threads = []
    for j in range(4):
        t = threading.Thread(target=final_test, args=(c_stub, r_stub, i, j, ))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

print('Obtiene el data_set.')
try:
    dataset = next(client_grpc(
        method=c_stub.GetDataSet,
        indices_parser=api_pb2.solvers__dataset__pb2.DataSet,
        partitions_message_mode_parser=True
    ))
    with open('dataset.bin', 'wb') as f:
        f.write(dataset.SerializeToString())
except Exception as e:
    print('e -> ', e)
finally: pass

print('waiting for kill solvers ...')
sleep(120)

# Stop Random cnf service.
next(client_grpc(
    method=g_stub.StopService,
    input=gateway_pb2.TokenMessage(token=random_cnf_service.token)
))
print('\n\nAll good?')