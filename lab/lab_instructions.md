# Laboratory Exercise on Software-Defined Networking (SDN) using P4Runtime

## Objectives
- Understand the principles of Software-Defined Networking (SDN) and the role of P4 in packet processing.
- Learn how to implement a simple SDN controller using P4Runtime.
- Experiment with dynamic path changes in a network topology.

## Prerequisites
- Basic knowledge of networking concepts, including Ethernet and IP protocols.
- Familiarity with Python programming.
- Understanding of P4 programming language and its components.

## Environment Setup
1. Ensure you have Python 3 installed on your machine.
2. Install the required Python dependencies by running:
   ```
   pip install -r controller/requirements.txt
   ```
3. Install the P4 compiler to compile the P4 program.

## Project Structure
The project consists of the following components:
- **P4 Program**: Located in `p4/path_switch.p4`, this file defines the packet processing logic for the switch.
- **SDN Controller**: Implemented in `controller/p4runtime_controller.py`, this program manages the switch and modifies forwarding paths.
- **Network Topology**: Defined in `topology/custom_topo.py`, this file sets up the network environment.
- **Build and Run Scripts**: Scripts in the `tools` directory facilitate the compilation of the P4 program and the execution of the network topology.

## Instructions
1. **Compile the P4 Program**:
   - Navigate to the `tools` directory and run the build script:
     ```
     cd tools
     ./build_p4.sh
     ```

2. **Run the Network Topology**:
   - Execute the topology script to set up the network:
     ```
     ./run_topology.sh
     ```

3. **Start the SDN Controller**:
   - Open a new terminal and run the controller program:
     ```
     python3 controller/p4runtime_controller.py
     ```

4. **Observe the Network Behavior**:
   - The controller will change the forwarding path between hosts H1 and H3 every 15 seconds. Monitor the output in the terminal to see the changes in action.

## Expected Outcomes
- Successful compilation of the P4 program without errors.
- The network topology should be established with hosts H1, H2, and H3 connected through the switch.
- The controller should dynamically change the forwarding path, demonstrating the flexibility of SDN.

## Troubleshooting
- If you encounter issues during compilation, ensure that the P4 compiler is correctly installed and accessible in your PATH.
- Check the Python dependencies if the controller fails to run.
- Review the topology script for any configuration errors if the network does not start as expected.

## Conclusion
This laboratory exercise provides hands-on experience with Software-Defined Networking using P4Runtime. By completing this exercise, you will gain a deeper understanding of how SDN enables dynamic network management and control.