import time
import argparse
from scapy.all import *


def main():
    """
    Capture network traffic using AsyncSniffer and save the captured packets to a pcap file.

    This function:
      - Parses command-line arguments to determine the output pcap file name.
      - Starts an asynchronous sniffer to capture packets.
      - Waits for a fixed duration to allow packet capture.
      - Stops the sniffer and writes the captured packets to the specified pcap file.

    :return: None
    :rtype: None
    """
    parser = argparse.ArgumentParser(description='OS agnostic universal recorder')
    parser.add_argument(
            '--pcap',
            type=str,
            required=True,
            help='the name of the pcap.',
    )
    args = parser.parse_args()

    t = AsyncSniffer()
    t.start()
    time.sleep(6)
    result = t.stop()

    wrpcap(args.pcap, result)


if __name__ == "__main__":
    main()
