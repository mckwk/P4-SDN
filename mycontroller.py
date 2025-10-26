import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))

from p4runtime_lib.switch import ShutdownAllSwitchConnections
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.bmv2 import Bmv2SwitchConnection
from p4runtime_lib.helper import P4InfoHelper
import argparse

import time
import grpc

PATHS = [
    # P1: s1 -> s3 -> s6
    {
        's1': (2, '00:00:00:00:02:03'),
        's3': (3, '00:00:00:00:03:06'),
        's6': (6, '00:00:00:00:06:03')
    },
    # P2: s1 -> s4 -> s5 -> s6
    {
        's1': (4, '00:00:00:00:02:04'),
        's4': (3, '00:00:00:00:04:05'),
        's5': (3, '00:00:00:00:05:06'),
        's6': (4, '00:00:00:00:06:03')
    },
    # P3: s1 -> s4 -> s6
    {
        's1': (4, '00:00:00:00:02:04'),
        's4': (4, '00:00:00:00:04:06'),
        's6': (5, '00:00:00:00:06:03')
    }
]


# Map switch name -> (gRPC address, device_id)
SWITCH_CONNECTIONS = {
    's1': ('127.0.0.1:50051', 0),
    's2': ('127.0.0.1:50052', 1),
    's3': ('127.0.0.1:50053', 2),
    's4': ('127.0.0.1:50054', 3),
    's5': ('127.0.0.1:50055', 4),
    's6': ('127.0.0.1:50056', 5)
}


DST_IP = '10.0.1.3'
DST_MASK = 32


def install_path(p4info_helper, switch_connections, path_map):
    for sw_name, (egress_port, next_hop_mac) in path_map.items():
        addr, device_id = SWITCH_CONNECTIONS[sw_name]
        print(f"Connecting to {sw_name} at {addr}")
        s = Bmv2SwitchConnection(name=sw_name, address=addr, device_id=device_id,
                                proto_dump_file=f'logs/{sw_name}-p4runtime-requests.txt')
        try:
            s.MasterArbitrationUpdate()
            s.SetForwardingPipelineConfig(p4info=p4info_helper.p4info, bmv2_json_file_path=args.bmv2_json)
        except grpc.RpcError as e:
            printGrpcError(e)
            continue

        table_entry = p4info_helper.buildTableEntry(
            table_name='MyIngress.ipv4_lpm',
            match_fields={'hdr.ipv4.dstAddr': (DST_IP, DST_MASK)},
            action_name='MyIngress.set_egress',
            action_params={'dmac': next_hop_mac, 'port': egress_port}
        )
        print(
            f"Writing entry to {sw_name}: dst {DST_IP}/{DST_MASK} -> port {egress_port}, mac {next_hop_mac}")
        s.WriteTableEntry(table_entry)


    print("All entries for path installed.")


def clear_all_entries(p4info_helper):
    for sw_name, (addr, device_id) in SWITCH_CONNECTIONS.items():
        try:
            s = Bmv2SwitchConnection(name=sw_name, address=addr, device_id=device_id)
            s.MasterArbitrationUpdate()
            s.SetForwardingPipelineConfig(
                p4info=p4info_helper.p4info, bmv2_json_file_path=args.bmv2_json)
            # read entries and delete matches for the dst
            for response in s.ReadTableEntries(table_id=p4info_helper.get_tables_id('MyIngress.ipv4_lpm')):
                for entity in response.entities:
                    s.DeleteTableEntry(entity)
        except Exception:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='P4Runtime rotating-path controller')
    parser.add_argument('--p4info', help='p4info file', required=False,
                        default='./build/simple_forwarding.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON',
                        required=False, default='./build/simple_forwarding.json')
    args = parser.parse_args()


    if not os.path.exists(args.p4info) or not os.path.exists(args.bmv2_json):
        print('Missing build artifacts. Compile the P4 program first (p4c) to generate p4info and bmv2 JSON in ./build/.')
        sys.exit(1)


    p4info_helper = P4InfoHelper(args.p4info)


    try:
        idx = 0
        while True:
            path_map = PATHS[idx % len(PATHS)]
            print(f"\n--- Installing path #{(idx % len(PATHS)) + 1} ---")
            install_path(p4info_helper, SWITCH_CONNECTIONS, path_map)
            print("Sleeping 15 seconds before next path rotation...")
            time.sleep(15)
            idx += 1
    except KeyboardInterrupt:
        print('\nInterrupted — cleaning up and exiting')
        ShutdownAllSwitchConnections()
