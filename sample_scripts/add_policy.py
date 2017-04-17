import gobgp_pb2
import sys

from grpc.beta import implementations
from grpc.framework.interfaces.face.face import ExpirationError

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


def create_community_sets(channel):
    com1 = gobgp_pb2.DefinedSet()
    com1.type = gobgp_pb2.COMMUNITY
    com1.name = "internal"
    com1.list.append("65000:1")

    com2 = gobgp_pb2.DefinedSet()
    com2.type = gobgp_pb2.COMMUNITY
    com2.name = "reject_internal"
    com2.list.append("65000:666")

    _call_grpc(channel, "AddDefinedSet", "AddDefinedSetRequest", set=com1)
    _call_grpc(channel, "AddDefinedSet", "AddDefinedSetRequest", set=com2)


def create_statements(channel):
    st1 = gobgp_pb2.Statement()
    st1.name = "reject_internal"

    st1.conditions.community_set.type = gobgp_pb2.ANY
    st1.conditions.community_set.name = "reject_internal"
    st1.actions.route_action = gobgp_pb2.REJECT

    st2 = gobgp_pb2.Statement()
    st2.name = "accept_internal"

    st2.conditions.community_set.type = gobgp_pb2.ANY
    st2.conditions.community_set.name = "internal"
    st2.actions.route_action = gobgp_pb2.ACCEPT

    _call_grpc(channel, "AddStatement", "AddStatementRequest", statement=st1)
    _call_grpc(channel, "AddStatement", "AddStatementRequest", statement=st2)


def create_policy(channel):
    p = gobgp_pb2.Policy()
    p.name = "export_internal"

    st1 = p.statements.add()
    st1.name = "reject_internal"

    st2 = p.statements.add()
    st2.name = "accept_internal"

    _call_grpc(channel, "AddPolicy", "AddPolicyRequest", policy=p, refer_existing_statements=True)


def assign_policy(channel):
    pa = gobgp_pb2.PolicyAssignment()
    pa.type = gobgp_pb2.EXPORT
    pa.resource = gobgp_pb2.GLOBAL
    pa.name = "asdasd"
    
    p1 = pa.policies.add()
    p1.name = "export_internal"

    pa.default = gobgp_pb2.REJECT

    _call_grpc(channel, "AddPolicyAssignment", "AddPolicyAssignmentRequest", assignment=pa)


def soft_reset_peers(channel):
    peers = _call_grpc(channel, "GetNeighbor", "GetNeighborRequest").peers

    for peer in peers:
        kwargs = {
            "address": peer.conf.neighbor_address,
            "direction": gobgp_pb2.SoftResetNeighborRequest.BOTH,
        }
        _call_grpc(channel, "SoftResetNeighbor", "SoftResetNeighborRequest", **kwargs)


def run(gobgpd_addr, gobgpd_port):
    channel = implementations.insecure_channel(gobgpd_addr, gobgpd_port)
    create_community_sets(channel)

    try:
        create_statements(channel)
    except Exception as e:
        if "is already set" not in e.details:
            raise

    create_policy(channel)
    assign_policy(channel)

    soft_reset_peers(channel)


if __name__ == '__main__':
    gobgp = sys.argv[1]
    port = int(sys.argv[2])
    run(gobgp, port)
