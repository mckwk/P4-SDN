import sys, os, time, grpc, argparse
from time import sleep

try:
    from p4.v1 import p4runtime_pb2
except ImportError:
    print("Warning: p4runtime_pb2 not found, assuming available in helper lib.")

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../utils/'))
from p4runtime_lib.switch import ShutdownAllSwitchConnections
from p4runtime_lib.helper import P4InfoHelper
from p4runtime_lib.error_utils import printGrpcError
import p4runtime_lib.bmv2


def modify_forwarding(switch, p4info_helper, dstAddr, dstMac, port):
    """
    Modifies the forwarding rule for a specific destination address on the switch.
    """
    try:
        # Build the table entry
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={"hdr.ipv4.dstAddr": (dstAddr, 32)},
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr": dstMac,
                "port": port
            }
        )

        switch.WriteTableEntry(table_entry)
        print(f"Forwarding rule updated on {switch.name}: {dstAddr} -> {dstMac} via port {port}")
    except grpc.RpcError as e:
        printGrpcError(e)


def main(p4info_file_path, bmv2_file_path):
    p4info_helper = P4InfoHelper(p4info_file_path)

    try:
        # Connect to the switches
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
        )
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
        )
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
        )
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
        )
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
        )

        # Perform master arbitration and set pipeline configuration
        for switch in [s1, s3, s4, s5, s6]:
            switch.MasterArbitrationUpdate()
            switch.SetForwardingPipelineConfig(p4info=p4info_helper.p4info, bmv2_json_file_path=bmv2_file_path)

        # Define paths
        paths = [
            {  # Path P1
                "s1": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 3},
                "s3": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 3},
                "s6": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 4}
            },
            {  # Path P2
                "s1": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 2},
                "s4": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 3},
                "s5": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 3},
                "s6": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 4}
            },
            {  # Path P3
                "s1": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 2},
                "s4": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 4},
                "s6": {"dstAddr": "10.0.2.2", "dstMac": "08:00:00:00:02:22", "port": 4}
            }
        ]

        # Cycle through paths every 15 seconds
        path_index = 0
        while True:
            print(f"Installing path P{path_index + 1}")
            for switch_name, rule in paths[path_index].items():
                switch = locals()[switch_name]
                modify_forwarding(switch, p4info_helper, rule["dstAddr"], rule["dstMac"], rule["port"])
            path_index = (path_index + 1) % len(paths)
            sleep(15)

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)
    finally:
        ShutdownAllSwitchConnections()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/basic.p4.p4info.txtpb')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/basic.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)

    main(args.p4info, args.bmv2_json)