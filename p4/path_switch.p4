// This P4 program defines the packet processing logic for the switch.
// It includes the parser for Ethernet and IPv4 headers, match-action tables for forwarding decisions, and actions for modifying packet headers.

#include <core.p4>
#include <v1model.p4>

parser MyParser(packet_in packet) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4; // IPv4
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

control MyIngress(inout headers hdr, inout metadata meta) {
    action set_nexthop(bit<48> mac) {
        hdr.ethernet.dstAddr = mac;
    }

    table forwarding {
        key = {
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            set_nexthop;
            NoAction;
        }
        default_action = NoAction;
    }

    apply {
        forwarding.apply();
    }
}

control MyEgress(inout headers hdr, inout metadata meta) {
    apply {
        // Egress processing can be added here if needed
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {
        // Checksum verification can be added here if needed
    }
}

control MyDeparser(packet_out packet) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

package MyPipeline {
    MyParser parser;
    MyIngress ingress;
    MyEgress egress;
    MyVerifyChecksum verifyChecksum;
    MyDeparser deparser;
}