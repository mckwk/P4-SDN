#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;

header ethernet_t { bit<48> dstAddr; bit<48> srcAddr; bit<16> etherType; }
header ipv4_t {
    bit<4> version; bit<4> ihl; bit<8> diffserv; bit<16> totalLen;
    bit<16> identification; bit<3> flags; bit<13> fragOffset;
    bit<8> ttl; bit<8> protocol; bit<16> hdrChecksum; bit<32> srcAddr; bit<32> dstAddr;
}

struct headers { ethernet_t ethernet; ipv4_t ipv4; }
struct metadata { }

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata){
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) { TYPE_IPV4: parse_ipv4; default: accept; }
    }
    state parse_ipv4 { packet.extract(hdr.ipv4); transition accept; }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action set_egress(bit<48> dmac, bit<9> port){
        hdr.ethernet.dstAddr = dmac;
        hdr.ethernet.srcAddr = hdr.ethernet.srcAddr;
        standard_metadata.egress_spec = port;
    }
    action drop() { mark_to_drop(standard_metadata); }

    table ipv4_lpm {
        key = { hdr.ipv4.dstAddr: lpm; }
        actions = { set_egress; drop; NoAction; }
        size = 1024; default_action = NoAction();
    }

    apply {
        if(hdr.ipv4.isValid()){
            if(hdr.ipv4.ttl==0){ drop(); return; }
            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
            ipv4_lpm.apply();
        }
    }
}

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) { apply { } }
control MyDeparser(packet_out packet, in headers hdr) { apply { packet.emit(hdr.ethernet); packet.emit(hdr.ipv4); } }
control MyVerifyChecksum(inout headers hdr, inout metadata meta) { apply { } }
control MyComputeChecksum(inout headers hdr, inout metadata meta) { apply { } }

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;
