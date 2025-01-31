# PQClass

Classification of Operation Systems and Browsers using Post-Quantum Cryptography Algorithms.

## Folder Structure

Each folder contains `.pcap` traffic recordings from various OSs and browsers that use or do not use PQC encryption. It also includes scripts that record the data, split it into flows, and collect the needed samples for the project.

The TDL folder contains a script that extracts the needed data (Time, Direction, Length) from each packet of the sample file and saves it to a `.csv` file. It also contains a script that merges all the `.csv` files into a large `.csv` file, later used as data to train and test our models.

## TDL

Inside each `.csv` file in the `TDL/` directory, each line represents a flow, each cell represents a packet, and is a list of 3 values.
- T: relative time (the time from the start of the flow to the current packet being sent in milliseconds).
- D: direction (0 - packet from the client to the server, 1 - packet from the server to the client).
- L: length (the size of the packet in bytes).

Example:

```text
[1, 40, 106] - D: From server to client / L: 40 bytes size / T: 106 milliseconds from the start of the flow.
[0, 1420, 102] - D: From client to server / L: 1420 bytes size / T: 102 milliseconds from the start of the flow.
```

## Classification Method

We're labeling files and samples according to the following method:

```text
PQC:
0 - Not Using PQC
1 - Using PQC

Browsers:
10 - Firefox
20 - Chrome

OS:
200 - Windows
300 - Linux
400 - MacOS

Examples:
311 - Linux / Firefox / Using PQC
420 - MacOS / Chrome / Not Using PQC
```

## Open Source Tools

To automate the process of opening the web browser we're using:

- For Windows: [AutoHotKey](https://www.autohotkey.com/) - Automation scripting language for Windows.
- For MacOS: [bash](https://www.gnu.org/software/bash/) script and [HammerSpoon](https://www.hammerspoon.org/) - Tool for automation of macOS.
- For Linux: [bash](https://www.gnu.org/software/bash/) script and [ydotool](https://github.com/ReimuNotMoe/ydotool) - Generic Linux command-line automation tool.

To automate the process of recording the traffic we're using:

- For Windows: [Scapy](https://scapy.net/) - Interactive packet manipulation library.
- For MacOS and Linux: [TCPDump](https://www.tcpdump.org/) - Packet analyzer.

For splitting the recorded traffic into each flow we're using:

- For Windows: [SplitCap](https://www.netresec.com/?page=SplitCap) - PCAP file splitter. 
- For MacOS: [Tshark](https://tshark.dev/) - Network Protocol Analyzer.
- For Linux: [Pkt2Flow](https://github.com/caesar0301/pkt2flow) - Utility to classify packets into flows.

To transform each packet into processable data we're using [NFStream](https://www.nfstream.org/) - Flexible Network Data Analysis Framework.

We run the models and analyze the data using [python](https://www.python.org/).

## Workflow

> [!NOTE]
> All the steps below take a few minutes to complete, so don't worry and be patient.

> [!IMPORTANT]
> Run the automation script in each folder on their corresponding operating system.

1. Run the automation script (`runner`) for each operating system, and wait until it finishes running.
2. Run the `tdl_runner.py` in the `TDL/` directory — this step will generate a `.csv` file with all the processed data from the pcaps you've recorded before.
3. Run `model-runner.py` in the main directory. This step trains and tests each model using the data generated in the previous step.
