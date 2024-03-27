from scapy.all import rdpcap
import pandas as pd           
import numpy as np             
from datetime import datetime

class SpeedTestConnection:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        self.connection_df = None
    def get_dataframe(self):
            """
            Assumes TCP packets only
            """
            packets = rdpcap(self.pcap_file)
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
            df['Time'] = df['Timestamp'].apply(epoch_to_datetime_string)

            df = df.sort_values(by='Time')
            # csv_file_path = "cached_data/" + self.pcap_file
            # df.to_csv(csv_file_path, index=False)

            return df

if __name__ == "__main__":
    print("SpeedTestConnection.py") 