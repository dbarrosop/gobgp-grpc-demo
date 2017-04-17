import gobgp_pb2
import sys

from grpc.beta import implementations
from grpc.framework.interfaces.face.face import ExpirationError

_TIMEOUT_SECONDS = 1


def run(gobgpd_addr, gobgpd_port, peer_address, peer_as):
    channel = implementations.insecure_channel(gobgpd_addr, gobgpd_port)

    peer = gobgp_pb2.Peer()
    peer.conf.neighbor_address = peer_address
    peer.conf.peer_as = peer_as

    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:
        try:
            stub.AddNeighbor(gobgp_pb2.AddNeighborRequest(peer=peer), _TIMEOUT_SECONDS)
        except ExpirationError, e:
            print str(e)
            sys.exit(-1)


if __name__ == '__main__':
    gobgp = sys.argv[1]
    port = int(sys.argv[2])
    peer_address = sys.argv[3]
    peer_as = int(sys.argv[4])

    run(gobgp, port, peer_address, peer_as)
