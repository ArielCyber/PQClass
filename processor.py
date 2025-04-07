import os
import sys
import socket
import ntpath
import shutil
import argparse
import subprocess
from scapy.all import *
from selenium import webdriver
import platform as platform_module
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

def path_leaf(path):
    """
    Return the final component of a pathname.

    :param path: The full file path.
    :type path: str
    :return: The last portion of the path.
    :rtype: str
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def loop_thru_all_files_in(path: str, ips: list[str]) -> tuple[int, str] | None:
    """
    Loop through all files in the specified directory and return the pcap file with the highest packet count that contains packets 
    with source or destination IP addresses matching any in the provided list.

    :param path: Directory path to scan for files.
    :type path: str
    :param ips: List of IP addresses to check against the packets.
    :type ips: list of str
    :return: A tuple containing the maximum packet count and the file path, or None if no matching file is found.
    :rtype: tuple(int, str) or None
    """
    print(ips)
    with os.scandir(path) as it:
        pcaps = []
        for entry in it:
            packets = rdpcap(entry.path)
            if entry.is_file and packets.filter(lambda packet: 
                           any(ip == packet[IP].src for ip in ips) or 
                           any(ip == packet[IP].dst for ip in ips)):
                pcaps.append((len(packets), entry.path))

        if len(pcaps) > 0:
            print(f'{max(pcaps) = }')
        return max(pcaps) if len(pcaps) > 0 else None


def split_streams(input_pcap: str, output_dir: str) -> None:
    """
    Extract TCP streams from a pcap file and save each stream to a separate pcap file in the specified output directory.

    :param input_pcap: Path to the input pcap file.
    :type input_pcap: str
    :param output_dir: Directory where the split pcap files will be stored.
    :type output_dir: str
    :raises subprocess.CalledProcessError: If the tshark command fails during extraction.
    :return: None
    :rtype: None
    """
    # Get unique stream IDs from the PCAP
    try:
        stream_ids = subprocess.check_output(
                f'tshark -r {input_pcap} -T fields -e tcp.stream'.split()
        ).decode().splitlines()

        # Remove duplicates and sort the stream IDs
        stream_ids = sorted(set(stream_ids))
        print(f"Found {len(stream_ids)} streams.")
    except subprocess.CalledProcessError as e:
        print(f"Error while extracting stream IDs: {e}")
        exit(1)

    os.mkdir(output_dir)
    # Extract each stream into a separate PCAP file
    for stream_id in stream_ids:
        if stream_id.strip():  # Ensure the stream_id is not empty
            output_pcap = os.path.join(output_dir, f"temp{stream_id}.pcap")
            print(f"Extracting stream ID {stream_id} to {output_pcap}")
            try:
                subprocess.run(
                        f'tshark -r {input_pcap} -w {output_pcap} -2 -R tcp.stream=={stream_id}'.split(),
                )
            except subprocess.CalledProcessError as e:
                print(f"Error while extracting stream ID {stream_id}: {e}")


def name_dir(browser: str, pqc: bool, algo: str | None) -> str:
    """
    Generate a directory name based on the browser, PQC flag, and chosen algorithm.
    Further explanation on the naming scheme can be found in README.md

    :param browser: The browser name (e.g., 'chrome' or 'firefox').
    :type browser: str
    :param pqc: Flag indicating whether PQC was used.
    :type pqc: bool
    :param algo: The chosen algorithm (e.g., 'mlkem' or 'kyber') or None.
    :type algo: str or None
    :return: A generated directory name based on input parameters.
    :rtype: str
    """
    naming_scheme = {
            None: 0,
            'firefox': 1,
            'chrome': 2,
            'Darwin': 4,
            'Linux': 3,
            'Windows': 2,
            'mlkem': 1,
            'kyber': 2,
    }
    
    # Backwards compatibility with original paper experiment
    
    return str(int(f'{naming_scheme[algo]}{naming_scheme[platform_module.system()]}{naming_scheme[browser]}{int(pqc)}'))


def open_browser(browser: str, pqc: bool, algo: str | None):
    """
    Open a web browser with specified settings and experimental options for PQC.

    :param browser: The browser to open ('chrome' or 'firefox').
    :type browser: str
    :param pqc: Flag indicating if PQC is being used.
    :type pqc: bool
    :param algo: The chosen algorithm ('mlkem' or 'kyber') or None.
    :type algo: str or None
    :return: An instance of Selenium WebDriver with the configured options.
    :rtype: selenium.webdriver.WebDriver
    """
    # Initialize options
    chrome_options = webdriver.ChromeOptions()
    firefox_options = webdriver.FirefoxOptions()
    
    chrome_local_state_prefs = {"browser": {"enabled_labs_experiments": []}}

    # Configure experimental options for PQC
    if pqc:
        # ALL browsers use MLKEM by default
        if algo == 'kyber':
            chrome_local_state_prefs["browser"]["enabled_labs_experiments"] = [
                "use-ml-kem@2"
            ]
    # Disable PQC for the browsers
    else:
        chrome_local_state_prefs["browser"]["enabled_labs_experiments"] = [
            "enable-tls13-kyber@2",
            "use-ml-kem@2"
        ]    
        firefox_options.set_preference('network.http.http3.enable_kyber', False)
        firefox_options.set_preference('security.tls.enable_kyber', False)
    
    chrome_options.add_experimental_option("localState", chrome_local_state_prefs)

    # Select driver based on browser type
    if browser == 'chrome':
        chrome_driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install() if platform_module.system() == 'Linux' else ChromeDriverManager().install()
        driver = webdriver.Chrome(service=ChromeService(chrome_driver_path), options=chrome_options)
    else:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)

    return driver


def main():
    """
    Main entry point for the script that records network traffic and extracts TCP streams.

    This function:
      - Parses command-line arguments.
      - Validates the conditions for the '--algo' argument based on the PQC flag.
      - Determines the final directory name and creates the directory.
      - Optionally prompts for sudo privileges on non-Windows systems.
      - Continuously captures network traffic using a sniffer script and a browser session until the desired amount of pcaps is recorded.
      - Splits the captured pcap into individual TCP streams and copies the pcap with sufficient packet count to the final directory.
      - Cleans up temporary files and directories.

    :return: None
    :rtype: None
    """
    # argument parser
    parser = argparse.ArgumentParser(description='OS agnostic universal network recording processor')
    parser.add_argument(
            '--browser',
            choices=['firefox', 'chrome'],
            type=str,
            required=True,
            help='the chosen browser.',
    )
    parser.add_argument(
            '--pqc',
            required=True,
            action=argparse.BooleanOptionalAction,
            help='was the session recorded using pqc or not.',
    )
    parser.add_argument(
            '--algo',
            choices=['mlkem', 'kyber'],
            type=str,
            required=False,
            help='the chosen algorithm.',
    )
    parser.add_argument(
            '--amount',
            type=int,
            required=True,
            help='amount the pcaps to be recorded in the sessions.',
    )
    parser.add_argument(
            '--domain',
            type=str,
            required=False,
            default='pq.cloudflareresearch.com'
    )
    args = parser.parse_args()

    # Conditional logic for --algo argument
    if args.pqc and not args.algo:
        parser.error('--algo is required when --pqc is provided.')
    if not args.pqc and args.algo:
        parser.error('--algo should not be provided with --no-pqc.')
    
    # start setup
    python_executable = path_leaf(sys.executable)
    print(f'{python_executable = }')

    addrs = socket.getaddrinfo(args.domain, None)
    ip_addrs: list[str] = list(set(addr[4][0] for addr in addrs))

    final_dir: str = name_dir(args.browser, args.pqc, args.algo)

    os.mkdir(final_dir)

    if platform_module.system() != 'Windows':
        print('this script will ask you for your sudo password.')
        print('please enter it now:')
        subprocess.run('sudo echo thank you, resuming...'.split())

    while (i := len(os.listdir(final_dir))) < args.amount:
        output_dir = f'temp-{i}'
        sniffed_pcap = f'sniff-{i}.pcap'

        sniff_command = f'{python_executable} sniffer.py --pcap {sniffed_pcap}'
        print(sniff_command)
        if platform_module.system() != 'Windows':
            sniff_command = f'sudo {sniff_command}'
        proc = subprocess.Popen(sniff_command.split())

        driver = open_browser(args.browser, args.pqc, args.algo)

        driver.get(f'https://{args.domain}')

        while proc.poll() is None:
            pass
        
        driver.quit()
        
        split_streams(sniffed_pcap, output_dir)

        length, pcap_path = loop_thru_all_files_in(output_dir, ip_addrs)
        if length > 20:
            shutil.copy2(pcap_path, f'{final_dir}/{i:02}.pcap')

        shutil.rmtree(output_dir, ignore_errors=True)
        os.remove(sniffed_pcap)


if __name__ == "__main__":
    main()
