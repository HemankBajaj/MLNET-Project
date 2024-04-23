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
            

            
            # Check if group has at least 20 packets and time difference is at least 9.9 seconds
            if len(df) < 20 or df.iloc[-1]['Timestamp'] - df.iloc[0]['Timestamp'] < 9.9:
                return 
            print(df.iloc[-1]['Timestamp'] - df.iloc[0]['Timestamp'])
            client_ip = df.iloc[0]['Source IP']
            server_ip = df.iloc[0]['Destination IP']

            n_groups = 20
            group_size = len(df) // n_groups
            group_dfs = [df.iloc[i:min(i+group_size, len(df))] for i in range(0, len(df), group_size)]

            cumulative_time = 0
            dict_grp = {
                    'Total Time': [],
                    'Upload Bytes': [],
                    'Download Bytes': [],
                    'Cumulative Time': []
            }
            
            for group_df in group_dfs:
                # Calculate total time for the group
                total_time = group_df.iloc[-1]['Timestamp'] - group_df.iloc[0]['Timestamp']

                # Calculate upload bytes
                upload_bytes = group_df[(group_df['Source IP'] == client_ip) & (group_df['Destination IP'] == server_ip)]['Length'].sum()

                # Calculate download bytes
                download_bytes = group_df[(group_df['Source IP'] == server_ip) & (group_df['Destination IP'] == client_ip)]['Length'].sum()

                # Update cumulative time
                cumulative_time += total_time
                print(total_time, type(total_time))
                # Append results
                dict_grp["Total Time"].append(float(total_time))
                dict_grp["Upload Bytes"].append(float(upload_bytes))
                dict_grp["Download Bytes"].append(float(download_bytes))
                dict_grp["Cumulative Time"].append(float(cumulative_time))

            df_conn = pd.DataFrame(dict_grp)

            directory = "cached_csv"
            
            # Check if the directory exists, if not, create it
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # save the CSV file into the directory
            file_name = os.path.basename(pcap_file)
            file_name = os.path.splitext(file_name)[0] # remove .gz
            file_name = os.path.splitext(file_name)[0] # remove .pcap
            csv_path = os.path.join(directory, file_name + ".csv")
            df_conn.to_csv(csv_path, index=False)

        cache_dataframe(pcap_file)



if __name__ == "__main__":
    data_directory = "../sample_data/20240301T000205.745148Z-pcap-mlab2-gru02-ndt/"
    pcap_list = readPCAP(data_directory)

    # caching the first 10 pcap files
    for i in range(10):
        conn = ConnectionCSV(pcap_list[i])
        print("OK")
    print("Cached Connection CSVs")