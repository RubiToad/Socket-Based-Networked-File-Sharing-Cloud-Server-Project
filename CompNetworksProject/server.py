import socket
from network_analysis import *  # add for timestamps
host = '10.142.0.2'
port = 3300
BUFFER_SIZE = 1024
dashes = '----> '
ntp_offset = get_time_offset()  # add for timestamps

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_tcp:
  server_tcp.bind((host,port))
  #tracking bytes recieved for upload speed calculation
  bytes_recieved = 0 
  #tracking bytes sent for download speed calculation 
  bytes_sent = 0
  while True:

    server_tcp.listen(6)
    print('[*] Waiting for connection')

    #establish client connection
    connection, addr = server_tcp.accept()
    with connection:
      print(f'[*] Accepted at {current_client_time(ntp_offset)}') # add for timestamps
      print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
      while True:
        #receive bytes
        data = connection.recv(BUFFER_SIZE)
        #add bytes recieved to tracker for upload speed calcuation
        bytes_recieved += len(data)
        #add bytes sent to tracker for download speed calculation
        bytes_sent += len(data)
        #verify received data
        if not data:
          break

        #split data and send time
        client_data = data.decode('utf-8').split('||')
        client_timestamp_str, client_message = client_data[0], client_data[1]
        client_timestamp = datetime.strptime(client_timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        server_receive_time = datetime.now() + timedelta(seconds=ntp_offset)

        #subtract send time from receive time
        time_difference = server_receive_time - client_timestamp
        print(f'[*] {server_receive_time} - Data received Test: {client_message}')
        print(f'[*] Time taken for data to send: {time_difference.total_seconds()} seconds')

        #convert to string
        #print('[*] Data received: {}'.format(data.decode('utf-8')))
        connection.send(dashes.encode('utf-8') + data)