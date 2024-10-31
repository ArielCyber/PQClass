# PQClass

Classification of Operation Systems and Browsers using Post-Quantum Cryptography Algorithms.

## Folder Structure

Each folder contains `.pcap` recording of traffic from various OS'/Browsers, while using/not using PQC encryption. They're also contain scripts that record the data, split it to flows, and collect the needed samples for the project.

The TDL folder contains a script that extracts the needed data (Time, Direction, Length) from each packet of the sample file, and saves it to a `.csv` file. It also contains a split that merges all the `.csv` file to a large `.csv` file, later used as data to train and test our models.

## Classification Method

We're labeling files and samples according to the following method:

```text
PQC:
0 - Not Using PQC
1 - Using PQC

Browsers:
10 - FireFox
20 - Chrome

OS:
200 - Windows
300 - Linux
400 - MacOS

Examples:
311 - Linux/Firefox/Using PQC
420 - Mac/Chrome/Not Using PQC
```

## Open Source Tools

In order to automate the process of opening the web browser we're using:

- For Windows: [AutoHotKey](https://www.autohotkey.com/) - Automation scripting language for Windows.
- For MacOS: [bash](https://www.gnu.org/software/bash/) script and [HammerSpoon](https://www.hammerspoon.org/) - Tool for automation of macOS.
- For Linux: [bash](https://www.gnu.org/software/bash/) script and [ydotool](https://github.com/ReimuNotMoe/ydotool) - Generic Linux command-line automation tool

In order to automate the process of recording the traffic we're using:

- For Windows: [Scapy](https://scapy.net/) - Interactive packet manipulation library.
- For MacOS and Linux: [TCPDump](https://www.tcpdump.org/) - Packet analyzer

For splitting the recorded traffic into each flow we're using:

- For Windows: [SplitCap](https://www.netresec.com/?page=SplitCap) - PCAP file splitter. 
- For MacOS: [Tshark](https://tshark.dev/) - Network Protocol Analyzer.
- For Linux: [Pkt2Flow](https://github.com/caesar0301/pkt2flow) - Utility to classify packets into flows.

In order to transform each packet into processable data we're using [NFStream](https://www.nfstream.org/) - Flexible Network Data Analysis Framework.

We're running the models and analyzing the data using [python](https://www.python.org/)

## Workflow

> [!NOTE]
> All the steps below take a few minutes to complete, so don't worry and be patient.

> [!IMPORTANT]
> Make sure to run the automation script in each folder on their corresponding operating system

1. Run the automation script (`runner`) for each operating system, wait until it finished running.
2. Run the `tdl-runner.py` in the `TDL/` directory - this step will generate a `.csv` file with all the processed data from the pcaps you've recorded before.
3. Run the `model-runnnner.py` - this step will train and test each model on the data generated in the previous step.
4. Run the `plotter.py` in the `ICC/` directory - this step will create graph of the accuracy over packet number for each model.

## Applications

iMessage, Signal, PQ Chat, Hybrid PQ VPN, Sunary, Sunbeam, Zoom
