import streamlit as st
from TestFramework import ConnectionDF, TestFramework
from FileIO import MatrixFileIO
from ConnectionCSV import readPCAP
import numpy as np

# Load Q-table
q_table = MatrixFileIO.read_matrix("q_table.txt")

# Function to run test on selected PCAP file
def run_test(pcap_file):
    connection_df = ConnectionDF(pcap_file)
    test_case = TestFramework(connection_df, q_table)
    test_case.simulate_test()
    upload_error, download_error, time_saved = test_case.get_results()
    return upload_error, download_error, time_saved

# Main Streamlit app
def main():
    st.title("PCAP Analysis Demo")

    # File upload section
    uploaded_file = st.file_uploader("Upload PCAP file", type=["pcap"])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")

        # Run test on uploaded file
        upload_error, download_error, time_saved = run_test(uploaded_file)

        # Display results
        st.write("Results:")
        st.write(f"Upload Error: {upload_error}")
        st.write(f"Download Error: {download_error}")
        st.write(f"Fraction of Time Saved: {time_saved}")

if __name__ == "__main__":
    main()
