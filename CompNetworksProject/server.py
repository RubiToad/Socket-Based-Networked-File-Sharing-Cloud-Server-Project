import socket
from datetime import datetime, timedelta
import os
from network_analysis import *  # add for timestamps

host = '10.128.0.3'
port = 3300
BUFFER_SIZE = 1024
dashes = '----> '
ntp_offset = get_time_offset()  # add for timestamps

#files are saved in uploads folder
UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def send_file(connection, file_name):
  """Send a file to the client."""
  file_path = os.path.join(UPLOAD_DIR, file_name)
  if not os.path.exists(file_path):
    connection.send(b'ERROR: File does not exist.')
    return False

  file_size = os.path.getsize(file_path)
  connection.send(b'READY')  # Acknowledge readiness to send

  # Send the file in chunks
  with open(file_path, 'rb') as file:
    while chunk := file.read(BUFFER_SIZE):
      connection.send(chunk)
  connection.send(b'DONE')  # Signal the end of the file transfer
  print(f"[*] File {file_name} sent successfully.")
  return True



def save_file(connection, file_name, file_size):
  #file saved to uploads folder
  received_size = 0
  with open(os.path.join(UPLOAD_DIR, file_name), 'wb') as f:
    while received_size < file_size:
      chunk = connection.recv(BUFFER_SIZE)
      if not chunk:
        break
      f.write(chunk)
      received_size += len(chunk)
  return received_size

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
        while True:
          # receive bytes
          data = connection.recv(BUFFER_SIZE)
          # add bytes received to tracker for upload speed calculation
          bytes_recieved += len(data)
          # add bytes sent to tracker for download speed calculation
          bytes_sent += len(data)
          # verify received data
          if not data:
            break

          try:
            message = data.decode('utf-8').split('||')
            command = message[0].split()[0]

            if command == "UPLOAD":
              # Existing upload logic (unchanged)
              metadata = message[0].split()
              file_name = metadata[1]
              file_size = int(metadata[2])
              file_type = metadata[3]
              connection.send(b'READY')  # Acknowledge readiness to receive
              saved_size = save_file(connection, file_name, file_size)
              if saved_size == file_size:
                print(f"[*] File {file_name} uploaded successfully.")
                connection.send(b'File uploaded successfully.')
              else:
                print("[!] File upload failed.")
                connection.send(b'File upload failed.')

            elif command == "DELETE":
              # Existing delete logic (unchanged)
              file_name = message[0].split()[1]
              file_path = os.path.join(UPLOAD_DIR, file_name)
              if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[*] File {file_name} deleted.")
                connection.send(f"File {file_name} deleted.".encode())
              else:
                print(f"[!] File {file_name} does not exist.")
                connection.send(f"File {file_name} does not exist.".encode())

            elif command == "DOWNLOAD":
              # New download logic
              file_name = message[0].split()[1]  # Extract the requested file name
              if send_file(connection, file_name):
                print(f"[*] File {file_name} sent successfully.")
              else:
                print(f"[!] File {file_name} could not be sent.")

            else:
              # Existing logic for other commands (e.g., time handling)
              client_timestamp_str, client_message = message
              client_timestamp = datetime.strptime(client_timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
              server_receive_time = datetime.now() + timedelta(seconds=ntp_offset)
              time_difference = server_receive_time - client_timestamp
              print(f"[*] {server_receive_time} - Data received: {client_message}")
              print(f"[*] Time taken for data transfer: {time_difference.total_seconds()} seconds")
              connection.send(dashes.encode('utf-8') + data)

          except Exception as e:
            print(f"[!] Error processing data: {e}")
            connection.send(b'ERROR: Unable to process request.')