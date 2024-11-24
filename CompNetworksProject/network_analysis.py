# network_analysis.py
import ntplib
from datetime import datetime, date, time, timedelta
#Step 6
"""
offset is the difference between local clock and  NTP server clock
which is the amount to correct the local clock by in seconds to 
match the clock of the NTP server.

offset = ((recv_timestamp - orig_timestamp) + (tx_timestamp - dest_timestamp))/2
"""
def get_time_offset():
    client = ntplib.NTPClient()
    server = '0.pool.ntp.org'
    try:
        resp = client.request(server, version=3)
    except Exception as e:
        print(e)
    return resp.offset

def current_client_time(ntp_offset):
    current_time = datetime.utcnow()
    new_datetime = current_time + timedelta(seconds=ntp_offset)
    return f'{new_datetime}'
    #print(get_time_offset())

# makes a calculation using the bytes recieved and time offset to get the upload speed in MB/s
def get_upload_speed(bytes_recieved, time_difference):
    if bytes_recieved == 0:
        return 0
    else:
        bytes_MB = bytes_recieved / (1024 * 1024)  # converts the bytes into MB
        upload_speed = bytes_MB / time_difference.total_seconds() # calculates the upload speed in MB/s
        return upload_speed

# makes a calculation using the bytes sent and time offset to get the download speed in MB/s
def get_download_speed(bytes_sent, time_difference):
    if bytes_sent == 0:
        return 0
    dlBytes_MB = bytes_sent / (1024 * 1024) # converts the bytes into MB
    download_speed = dlBytes_MB / time_difference.total_seconds() # calculates the download speed in MB/s
    return download_speed 

def get_packet_loss(sent,recieved):
    if sent == 0:
        return 0
    else:
        return (sent - recieved) / sent * 100

def get_network_stats(bytes_recieved,bytes_sent, packets_sent, packets_recieved, time_difference):
    stats = {1: f"Upload speed: {get_upload_speed(bytes_recieved,time_difference)} MB/s",
             2: f"Download speed: {get_download_speed(bytes_sent,time_difference)} MB/s ",
             3: f"File transfer time: {time_difference.total_seconds()} Seconds" ,
             4: f"Packets lost: {get_packet_loss(packets_sent,packets_recieved)}"
            }
    return stats