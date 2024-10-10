#Requires AutoHotkey v2.0

Loop 30
{

	Run 'C:/Users/Eylon/Desktop/ios_safari_nopqc/SplitCap.exe -r ios_safari_' . A_Index . '.pcap -o temp-' . A_Index ,, 'Hide'
	
}

Run 'python collector.py --ip 162.159.138.85 162.159.137.85 --browser safari --no-pqc'