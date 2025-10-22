#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import argparse
import os
import sys
from time import sleep

import grpc

# Import P4Runtime lib from parent utils dir
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.switch import ShutdownAllSwitchConnections


SWITCH_TO_HOST_PORT = 1
SWITCH_TO_SWITCH_PORT = 2


def writeTunnelRules(p4info_helper, ingress_sw, egress_sw, tunnel_id,
                     dst_eth_addr, dst_ip_addr):
    """
    Installs three rules:
    1) Tunnel ingress rule on the ingress switch.
    2) Tunnel transit rule on the ingress switch.
    3) Tunnel egress rule on the egress switch.
    """
    # 1) Tunnel Ingress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.myTunnel_ingress",
        action_params={
            "dst_id": tunnel_id,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print(f"Installed ingress tunnel rule on {ingress_sw.name}")

    # 2) Tunnel Transit Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_forward",
        action_params={
            "port": SWITCH_TO_SWITCH_PORT
        })
    ingress_sw.WriteTableEntry(table_entry)
    print(f"Installed transit tunnel rule on {ingress_sw.name}")

    # 3) Tunnel Egress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="MyIngress.myTunnel_egress",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": SWITCH_TO_HOST_PORT
        })
    egress_sw.WriteTableEntry(table_entry)
    print(f"Installed egress tunnel rule on {egress_sw.name}")


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.
    """
    print(f'\n----- Reading tables rules for {sw.name} -----')
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print(f'{table_name}: ', end='')
            for m in entry.match:
                print(f'{p4info_helper.get_match_field_name(table_name, m.field_id)} '
                      f'{p4info_helper.get_match_field_value(m)}', end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print(f'-> {action_name}', end=' ')
            for p in action.params:
                print(f'{p4info_helper.get_action_param_name(action_name, p.param_id)} '
                      f'{p.value}', end=' ')
            print()


def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch.
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print(f"{sw.name} {counter_name} {index}: "
                  f"{counter.data.packet_count} packets "
                  f"({counter.data.byte_count} bytes)")


# Updated controller logic for dynamic path switching
import time

def dynamicPathSwitching(p4info_helper, switches, paths):
    current_path_index = 0
    while True:
        current_path = paths[current_path_index]
        print(f"Switching to path: {current_path}")
        for i in range(len(current_path) - 1):
            ingress_sw = switches[current_path[i]]
            egress_sw = switches[current_path[i + 1]]
            # Update table entries for the current path
            writeTunnelRules(p4info_helper, ingress_sw, egress_sw, tunnel_id=100,
                             dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2")
        current_path_index = (current_path_index + 1) % len(paths)
        time.sleep(15)


def main(p4info_file_path, bmv2_file_path):
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create switch connections
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')

        # Establish master arbitration
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()

        # Install the P4 program
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program on s2")

        # Write tunnel rules
        writeTunnelRules(p4info_helper, ingress_sw=s1, egress_sw=s2, tunnel_id=100,
                         dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2")
        writeTunnelRules(p4info_helper, ingress_sw=s2, egress_sw=s1, tunnel_id=200,
                         dst_eth_addr="08:00:00:00:01:11", dst_ip_addr="10.0.1.1")

        # Read table entries
        readTableRules(p4info_helper, s1)
        readTableRules(p4info_helper, s2)

        # Print counters periodically
        while True:
            sleep(2)
            print('\n----- Reading tunnel counters -----')
            printCounter(p4info_helper, s1, "MyIngress.ingressTunnelCounter", 100)
            printCounter(p4info_helper, s2, "MyIngress.egressTunnelCounter", 100)
            printCounter(p4info_helper, s2, "MyIngress.ingressTunnelCounter", 200)
            printCounter(p4info_helper, s1, "MyIngress.egressTunnelCounter", 200)

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        print("gRPC Error:", e.details())

    ShutdownAllSwitchConnections()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.p4.p4info.txtpb')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print(f"\np4info file not found: {args.p4info}\nHave you run 'make'?")
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print(f"\nBMv2 JSON file not found: {args.bmv2_json}\nHave you run 'make'?")
        parser.exit(1)
    main(args.p4info, args.bmv2_json)