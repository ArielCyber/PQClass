#Requires AutoHotkey v2.0

Loop 20
{
	Run 'python sniffer.py ' . A_Index ,, 'Hide'

	Run '"C:/Program Files/Mozilla Firefox/firefox.exe" "https://pq.cloudflareresearch.com"',, 'Max'

	Sleep 4000

	Send '^w'

	Sleep 4000

	Run 'C:/Users/Eylon/PQC/windows/SplitCap.exe -r sniff' . A_Index . '.pcap -o temp-' . A_Index ,, 'Hide'
	
	Sleep 3000
}

Run 'python collector.py --ip 2606:4700:7::a29f:8a55 2606:4700:7::a29f:8955 --browser firefox --pqc'