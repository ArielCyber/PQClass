import sys
import time
from scapy.all import *


def main():
    t = AsyncSniffer()
    t.start()
    time.sleep(4)
    result = t.stop()

    wrpcap(f'sniff{sys.argv[1]}.pcap', result)


if __name__ == "__main__":
    main()
