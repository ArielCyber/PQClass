#!/usr/bin/env python3

from scapy.all import *
import os
import shutil
import argparse


def loop_thru_all_files_in(path: str, ips: list[str]) -> tuple[int, str] | None:
    with os.scandir(path) as it:
        pcaps = []
        #  pcaps = [
        #   (len(rdpcap(entry.path)), entry.path)
        #  for entry in it
        # if entry.is_file() and (any(ip in entry.path for ip in ips) or any(ip.replace('.', '-') in entry.path for ip in ips))
        # ]
        for entry in it:
            print(entry.path)
            if entry.is_file() and (any(ip in entry.path for ip in ips) or any(ip.replace(':', '-') in entry.path for ip in ips)):
                print("hello")
                packets = rdpcap(entry.path)
                pcaps.append((len(packets), entry.path))

        if len(pcaps) > 0:
            print(f'{max(pcaps) = }')
        return max(pcaps) if len(pcaps) > 0 else None


def loop_thru_all_dirs_in(path: str, ips: list[str], browser: str, pqc: bool) -> None:
    os.mkdir(f'{browser}_{pqc}')
    pcaps = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.name.startswith('temp-') and entry.is_dir():
                pcaps.append(loop_thru_all_files_in(f'{entry.path}', ips))
    for i, pcap_tup in enumerate(pcaps):
        if pcap_tup is not None:
            length, pcap_path = pcap_tup
            if length > 20:
                shutil.copy2(pcap_path, f'{path}/{browser}_{pqc}/{i:02}.pcap')


def main() -> None:
    cwd = os.getcwd()
    parser = argparse.ArgumentParser('Script to fliter the relevant packets')
    parser.add_argument('--ip', nargs='+', required=True, help='the ip(s) to filer by.')
    parser.add_argument(
        '--browser',
        required=True,
        type=str,
        help='the browser that was tested.'
    )
    parser.add_argument('--pqc', required=True, action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    loop_thru_all_dirs_in(cwd, args.ip, args.browser, args.pqc)


if __name__ == "__main__":
    main()
