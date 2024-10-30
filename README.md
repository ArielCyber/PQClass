# PQClass

PQClass - Classification of Operation Systems and Browsers using Post-Quantum Cryptography Algorithms.

## Folder Structure

Each folder contains `.pcap` recording of traffic from various OS'/Browsers, while using/not using PQC encryption. They're also contain scripts that record the data, split it to flows, and collect the needed samples for the project.

The TDL folder contains a script that extracts the needed data (Time, Direction, Length) from each packet of the sample file, and saves it to a `.csv` file. It also contains a split that merges all the `.csv` file to a large `.csv` file, later used as data to train and test our models.

## Classification Method

We're labeling files and samples according to the following method:

```text
PQC:
0 - Non-PQC
1 - PQC

Browsers:
10 - FireFox
20 - Chrome
30 - Safari
40 - iMessage

OS:
Windows - 200
Linux - 300
MacOS - 400
Android - 500
iOS - 600

Examples:
531 - Android/Safari/PQC
420 - Mac/Chrome/Non-PQC
```

## Open Source Tools

We're using [SplitCap](https://www.netresec.com/?page=SplitCap) in order to get the neede flows from the recording.

## Applications
iMessage, 
Signal, 
PQ Chat, 
Hybrid PQ VPN, 
Sunary, 
Sunbeam, 
Zoom
