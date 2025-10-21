# P4 Forwarding Project

## Overview
This project implements a packet forwarding logic using the P4 programming language. It includes a control plane written in Python and scripts for running the P4 program.


## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone [<repository-url>](https://github.com/mckwk/P4-SDN)
   cd p4-forwarding
   ```

2. **Install dependencies**:
   Make sure you have Python and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the P4 program**:
   Use the Makefile to compile the P4 program:
   ```bash
   make
   ```

4. **Run the behavioral model**:
   Execute the provided shell script to run the P4 program on the bmv2 simulator:
   ```bash
   ./tools/run_bmv2.sh
   ```

## Usage
- The P4 program in `src/forwarding.p4` defines the packet processing logic.
- The control plane in `control-plane/controller.py` manages flow entries and events.
