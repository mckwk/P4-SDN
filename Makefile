# Makefile for P4 Forwarding Project

# Define the P4 compiler and the behavioral model simulator
P4C = p4c
BMV2 = bmv2

# Define the source files
SRC = src/forwarding.p4
OUTPUT = build/forwarding.json

# Define the test files
TESTS = tests/test_forwarding.py

# Define the Python requirements
REQUIREMENTS = requirements.txt

# Default target
all: compile

# Compile the P4 program
compile:
	$(P4C) $(SRC) -o $(OUTPUT)

# Clean up build artifacts
clean:
	rm -rf build/*
	rm -f $(OUTPUT)

# Install Python dependencies
install:
	pip install -r $(REQUIREMENTS)

.PHONY: all compile clean install