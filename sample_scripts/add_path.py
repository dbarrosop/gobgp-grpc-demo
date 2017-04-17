import gobgp_pb2
import sys

from grpc.beta import implementations
from grpc.framework.interfaces.face.face import ExpirationError

from cgopy import *

_TIMEOUT_SECONDS = 1


def _call_grpc(channel, api_method, api_request, **kwargs):
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:
        try:
            api = getattr(stub, api_method)
            request = getattr(gobgp_pb2, api_request)
            return api(request(**kwargs), _TIMEOUT_SECONDS)
        except ExpirationError, e:
            print str(e)
            sys.exit(-1)


def create_path(channel, nlri, nexthop, community, med):
    af = 6
    prefix = nlri

    attrs = {
        "nexthop": nexthop,
        "community": community,
        "med": med,
    }
    
    path_attrs = " ".join(["{} {}".format(k, v) for k, v in attrs.items()])
    joined_args = "{} {}".format(prefix, path_attrs)

    serialized_path = libgobgp.serialize_path(libgobgp.get_route_family(_AF_NAME[af]), joined_args, ).contents
    # nlri
    nlri = unpack_buf(serialized_path.nlri)
    # pattrs
    pattrs = []
    for pattr_p in serialized_path.path_attributes.contents[:serialized_path.path_attributes_len]:
        pattrs.append(unpack_buf(pattr_p.contents))
    # path dict
    path = {"nlri": nlri, "pattrs": pattrs}


    afi = 2
    safi = 1
    # two octets for AFI, 1 octet for SAFI
    path["family"] = afi << 16 | safi

    kwargs = {
        "resource": gobgp_pb2.GLOBAL,
        "path": path,
    }
    _call_grpc(channel, "AddPath", "AddPathRequest", **kwargs)


def soft_reset_peers(channel):
    peers = _call_grpc(channel, "GetNeighbor", "GetNeighborRequest").peers

    for peer in peers:
        kwargs = {
            "address": peer.conf.neighbor_address,
            "direction": gobgp_pb2.SoftResetNeighborRequest.BOTH,
        }
        _call_grpc(channel, "SoftResetNeighbor", "SoftResetNeighborRequest", **kwargs)


def run(gobgpd_addr, gobgpd_port, prefix, nexthop, community, med):
    channel = implementations.insecure_channel(gobgpd_addr, gobgpd_port)

    create_path(channel, prefix, nexthop, community, med)

    soft_reset_peers(channel)




if __name__ == '__main__':
    gobgp = sys.argv[1]
    port = int(sys.argv[2])
    prefix = sys.argv[3]
    nexthop = sys.argv[4]
    community = sys.argv[5]
    med = int(sys.argv[6])

    run(gobgp, port, prefix, nexthop, community, med)
