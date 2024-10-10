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

  open -a "$1" https://$2 &

  sleep 4

  hs -c 'hs.application.launchOrFocus("$1")'
  hs -c 'hs.eventtap.keyStroke({"cmd"}, "w")'

  sudo killall tcpdump

  for stream in `tshark -r temp"$i".pcap -T fields -e tcp.stream | sort -n | uniq`
  do
    echo $stream
    tshark -r temp$i.pcap -w stream-$stream.pcap -2 -R "tcp.stream==$stream"
  done

  mkdir temp-$i
  
  mv stream* temp-$i
done

./collector.py --ip $(host $2 | grep 'has address' | awk '{ print $4 }' | tr '\n' ' ') --browser $1 $3

rm -rf temp*
