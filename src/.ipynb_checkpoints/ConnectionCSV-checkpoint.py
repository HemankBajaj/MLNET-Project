from scapy.all import rdpcap
import pandas as pd           
import numpy as np             
from datetime import datetime
import os 

def readPCAP(directory):   
    """
    Inputs a directory and retrieves all the pcap files inside that directory by recursively travelling it
    """
    def list_pcap_files(folder):
        pcap_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".pcap.gz"):
                    pcap_files.append(os.path.join(root, file))
        return pcap_files

    return list_pcap_files(directory)


class ConnectionCSV:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        def cache_dataframe(pcap_file):
            """
            Assumes TCP packets only
            """
            packets = rdpcap(pcap_file)
            # Extract fields from each packet
            fields_list = []
            for pkt in packets:
                if pkt.haslayer('UDP') or not pkt.haslayer('IP'):
                        continue
                if pkt.haslayer('TCP') and len(pkt['TCP'].payload) > 0:
                    ip = pkt['IP']
                    tcp = pkt['TCP']
                    fields_list.append([pkt.time, ip.src, ip.dst, ip.len, ip.proto, 'TCP', tcp.sport, tcp.dport, len(tcp.payload), tcp.chksum])
            
            # Create DataFrame
            df = pd.DataFrame(fields_list, columns=['Timestamp', 'Source IP', 'Destination IP', 'Length', 'Protocol', 'Transport Protocol', 'Source Port', 'Destination Port', 'Payload Length', 'Checksum'])
    
            def epoch_to_datetime_string(epoch_time):
                dt_obj = datetime.fromtimestamp(int(epoch_time))            
                datetime_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                return datetime_str
            # Time in readable format
            df['Time'] = df['Timestamp'].apply(epoch_to_datetime_string)

            # For now, assume that the df is sorted?
            # df = df.sort_values(by='Time')

            directory = "cached_csv"
            
            # Check if the directory exists, if not, create it
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # save the CSV file into the directory
            file_name = os.path.basename(pcap_file)
            file_name = os.path.splitext(file_name)[0]
            csv_path = os.path.join(directory, file_name + ".csv")
            df.to_csv(csv_path, index=False)

        cache_dataframe(pcap_file)


if __name__ == "__main__":
    data_directory = "../sample_data/20240301T000205.745148Z-pcap-mlab2-gru02-ndt/"
    pcap_list = readPCAP(data_directory)

    # caching the first 10 pcap files
    for i in range(10):
        conn = ConnectionCSV(pcap_list[i])
    print("Cached Connection CSVs")

        
        
        
        
        