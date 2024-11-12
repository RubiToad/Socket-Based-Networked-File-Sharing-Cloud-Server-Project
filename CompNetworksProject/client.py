import socket
from network_analysis import *

host = '35.196.227.253'
port = 3300



BUFFER_SIZE = 1024
ntp_offset = get_time_offset()
def setup_connection(message):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
    client_tcp.connect((host, port))

    #get time and seperate it from other data
    client_send_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
    client_send_time_str = client_send_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    data_to_send = f"{client_send_time_str}||{message}"
    #convert str to bytes
    client_tcp.send(data_to_send.encode('utf-8')) # byte object required
    data = client_tcp.recv(BUFFER_SIZE)
    yield print(f'The message received from the server: {data.decode("utf-8")}')
    yield print(f'The upload speed was: {get_upload_speed} MB/s')
    yield print(f'The download speed was: {get_download_speed} MB/s')

if __name__ == '__main__':
  while True:
    message = input('enter a message or q for quit: ')
    if message == 'q':
      quit()
    next(setup_connection(message))