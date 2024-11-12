# network_analysis.py
import ntplib
from datetime import datetime, date, time, timedelta
from server import bytes_recieved, time_difference
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
    current_date = datetime.now().date()
    initial_time = datetime.now().time()
    datetime_combination = datetime.combine(current_date, initial_time)
    new_datetime = datetime_combination + timedelta(seconds=ntp_offset)
    return f'{new_datetime}'
    #print(get_time_offset())

# makes a calculation using the time offset to get the upload speed in MB/s
def get_upload_speed(bytes_recieved, time_difference):
    bytes_MB = bytes_recieved / (1024 * 1024)  # converts the bytes into MB/s

    speed = bytes_MB / time_difference # gets the speed in MB/s
    return speed
