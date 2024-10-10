#!/usr/bin/env bash

usage()
{
  echo "Usage: $0 browser (eg. firefox) domain (eg. pq.cloudflareresearch.com) --pqc/--no-pqc"
  exit 1
}

if [ $# -ne 3 ] ; then
    usage
fi

echo this script will ask you for your sudo password.
echo please enter it now
sudo echo thank you, resuming...

for i in {1..20}
do
  sudo tcpdump -w temp"$i".pcap &

  $1 https://$2 &

  sleep 4

  ydotool key 29:1 17:1 29:0 17:0

  sudo killall tcpdump

  pkt2flow -o temp-"$i" temp"$i".pcap
done

./collector.py --ip $(host $2 | grep 'has address' | awk '{ print $4 }' | tr '\n' ' ') --browser $1 $3

rm -rf temp*
