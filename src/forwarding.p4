// This file contains the P4 program that defines the packet forwarding logic.
// It includes the necessary tables, actions, and control flow for processing packets.

#include <core.p4>
#include <v1model.p4>

const bit<48> DEFAULT_MAC = 0x000000000000;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

struct headers {
    ethernet_t ethernet;
}

struct metadata {
}

parser MyParser(packet_in pkt,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4;
            0x0806: accept;
            default: accept;
        }
    }
    state parse_ipv4 {
        transition accept;
    }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action forward(bit<9> port) {
        standard_metadata.egress_spec = port;
    }

    table forwarding_table {
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        actions = {
            drop;
            forward;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
        if (hdr.ethernet.isValid()) {
            if (hdr.ethernet.dstAddr == DEFAULT_MAC) {
                drop();
            } else {
                forwarding_table.apply();
            }
        }
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

control MyDeparser(packet_out pkt, in headers hdr) {
    apply {
        pkt.emit(hdr.ethernet);
    }
}

V1Switch(MyParser(), VerifyChecksum(), MyIngress(), MyEgress(), ComputeChecksum(), MyDeparser()) main;