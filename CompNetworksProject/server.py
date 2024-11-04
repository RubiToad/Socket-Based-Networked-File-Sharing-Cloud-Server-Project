import socket
#from ntp_offset_module import *  # add for timestamps
host = '10.162.0.2'
port = 3300
BUFFER_SIZE = 1024
dashes = '----> '
#ntp_offset = get_time_offset()  # add for timestamps

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_tcp:
  server_tcp.bind((host,port))

  while True:
    server_tcp.listen(6)
    print('[*] Waiting for connection')
    #establish client connection
    connection, addr = server_tcp.accept()
    with connection:
#print(f'[*] Accepted at {current_client_time(ntp_offset)}') # add for timestamps
      print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
      while True:
        #receive bytes
        data = connection.recv(BUFFER_SIZE)
        #veryify received data
        if not data:
          break
        else:
          #convert to string
          print('[*] Data received: {}'.format(data.decode('utf-8')))
        connection.send(dashes.encode('utf-8') + data)