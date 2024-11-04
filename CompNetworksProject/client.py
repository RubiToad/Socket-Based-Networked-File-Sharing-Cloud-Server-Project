import socket

host = '34.47.7.59'
port = 3300


BUFFER_SIZE = 1024

def setup_connection():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
    client_tcp.connect((host,port))
    #convert str to bytes
    client_tcp.send(message.encode('utf-8')) # byte object required
    data = client_tcp.recv(BUFFER_SIZE)
    yield print(f'The message received from the server: {data.decode("utf-8")}')

if __name__ == '__main__':
  while True:
    message = input('enter a message or q for quit: ')
    if message == 'q':
      quit()
    next(setup_connection())