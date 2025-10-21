#!/bin/bash

# This script compiles the P4 program into the necessary artifacts using the P4 compiler.

# Define the P4 source file and output directory
P4_SRC="../p4/path_switch.p4"
OUTPUT_DIR="../build"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Compile the P4 program
p4c-bm2-ss --json $OUTPUT_DIR/path_switch.json --p4runtime-file $OUTPUT_DIR/path_switch.p4info $P4_SRC

echo "P4 program compiled successfully. Artifacts are located in $OUTPUT_DIR."