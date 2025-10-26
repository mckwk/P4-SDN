import sys, os, time, grpc, argparse

try:
    from p4.v1 import p4runtime_pb2
except ImportError:
    print("Warning: p4runtime_pb2 not found, assuming available in helper lib.")

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../utils/'))
from p4runtime_lib.switch import ShutdownAllSwitchConnections
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.bmv2 import Bmv2SwitchConnection
from p4runtime_lib.helper import P4InfoHelper

DST_IP = '10.0.1.2'
DST_MASK = 32
H2_MAC = '08:00:00:00:02:02'

PATHS = [
    {'s1': (2, '00:00:00:03:00:01'), 's3': (2, '00:00:00:06:00:01'), 's6': (6, H2_MAC)},
    {'s1': (3, '00:00:00:04:00:01'), 's4': (2, '00:00:00:05:00:01'), 's5': (2, '00:00:00:06:00:02'), 's6': (6, H2_MAC)},
    {'s1': (3, '00:00:00:04:00:01'), 's4': (3, '00:00:00:06:00:03'), 's6': (6, H2_MAC)}
]

SWITCH_CONNECTIONS = {
    's1': ('127.0.0.1:50051', 0),
    's3': ('127.0.0.1:50053', 2),
    's4': ('127.0.0.1:50054', 3),
    's5': ('127.0.0.1:50055', 4),
    's6': ('127.0.0.1:50056', 5)
}

def connect_all_switches(p4info_helper, bmv2_json_file):
    switches = {}
    for sw_name, (addr, device_id) in SWITCH_CONNECTIONS.items():
        s = Bmv2SwitchConnection(name=sw_name, address=addr, device_id=device_id)
        s.MasterArbitrationUpdate()
        s.SetForwardingPipelineConfig(p4info=p4info_helper.p4info, bmv2_json_file_path=bmv2_json_file)
        switches[sw_name] = s
    return switches

def install_path(p4info_helper, switches_map, path_map):
    for sw_name, (port, mac) in path_map.items():
        s = switches_map.get(sw_name)
        if not s:
            print(f"no connection for {sw_name}", flush=True)
            continue
        print(f"Installing on {sw_name}: port={port}, mac={mac}", flush=True)
        entry = p4info_helper.buildTableEntry(
            table_name='MyIngress.ipv4_lpm',
            match_fields={'hdr.ipv4.dstAddr': (DST_IP, DST_MASK)},
            action_name='MyIngress.set_egress',
            action_params={'dmac': mac, 'port': port}
        )
        try:
            s.WriteTableEntry(entry, p4runtime_pb2.Update.MODIFY)
        except grpc.RpcError as e:
            if 'NOT_FOUND' in str(e):
                s.WriteTableEntry(entry, p4runtime_pb2.Update.INSERT)
            else:
                printGrpcError(e)

def clear_all_entries(p4info_helper, switches_map):
    for sw_name, s in switches_map.items():
        print(f"Clearing entries on {sw_name}", flush=True)
        table_id = p4info_helper.get_tables_id('MyIngress.ipv4_lpm')
        for response in s.ReadTableEntries(table_id=table_id):
            for entity in response.entities:
                if entity.HasField("table_entry"):
                    s.WriteTableEntry(entity.table_entry, p4runtime_pb2.Update.DELETE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime rotating-path controller')
    parser.add_argument('--p4info', default='./build/sdn_grpc.p4.p4info.txtpb')
    parser.add_argument('--bmv2-json', default='./build/sdn_grpc.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info) or not os.path.exists(args.bmv2_json):
        print("Missing build artifacts")
        sys.exit(1)

    p4info_helper = P4InfoHelper(args.p4info)
    switches = connect_all_switches(p4info_helper, args.bmv2_json)
    install_path(p4info_helper, switches, PATHS[0])
    print("--- First path installed ---", flush=True)

    # Rotate paths every 15s
    idx = 1
    try:
        while True:
            path_map = PATHS[idx % len(PATHS)]
            print(f"Rotating to path {idx % len(PATHS)}", flush=True)
            install_path(p4info_helper, switches, path_map)
            time.sleep(15)
            clear_all_entries(p4info_helper, switches)
            idx += 1
    except KeyboardInterrupt:
        ShutdownAllSwitchConnections()
