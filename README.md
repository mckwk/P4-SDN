# Software-Defined Networking (SDN) Laboratory Exercise

This project demonstrates a Software-Defined Networking (SDN) setup using P4Runtime. The goal is to create a network topology where packet forwarding paths can be dynamically changed by a controller program.

## Project Structure

```
p4runtime-sdn-lab
├── p4
│   └── path_switch.p4
├── controller
│   ├── p4runtime_controller.py
│   └── requirements.txt
├── topology
│   └── custom_topo.py
├── tools
│   ├── build_p4.sh
│   └── run_topology.sh
├── lab
│   └── lab_instructions.md
├── Makefile
├── .gitignore
└── README.md
```

## Setup Instructions

1. **Install Dependencies**: Ensure you have Python 3 installed. Navigate to the `controller` directory and install the required Python packages listed in `requirements.txt`:

   ```
   pip install -r requirements.txt
   ```

2. **Compile the P4 Program**: Before running the controller, compile the P4 program located in the `p4` directory. Use the provided shell script in the `tools` directory:

   ```
   cd tools
   ./build_p4.sh
   ```

3. **Run the Network Topology**: Set up the network topology using the provided script:

   ```
   ./run_topology.sh
   ```

4. **Start the Controller**: In a separate terminal, run the SDN controller to manage the network:

   ```
   cd controller
   python p4runtime_controller.py
   ```

## Usage

The controller will periodically change the forwarding path between hosts H1 and H3 every 15 seconds. You can observe the packet forwarding behavior by monitoring the network traffic between these hosts.

## Contributions

Contributions to this project are welcome. Please feel free to submit issues or pull requests for improvements or additional features.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.