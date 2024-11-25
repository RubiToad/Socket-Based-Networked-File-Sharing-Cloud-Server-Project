import socket
import threading
from datetime import datetime, timedelta
import os
from network_analysis import *  # add for timestamps

host = '0.0.0.0'
port = 3300
BUFFER_SIZE = 1024
dashes = '----> '
ntp_offset = get_time_offset()  # add for timestamps

#files are saved in uploads folder
UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)



#collect network stats and send it back to the client for display
def send_network_stats(connection,bytes_received,bytes_sent,packets_received,packets_sent,time_difference):
  network_stats = get_network_stats(bytes_received, bytes_sent, packets_received,packets_sent,time_difference)
  stats_to_send = []
  for key,value in network_stats.items():
    stats_to_send.append(f"{key}: {value}\n")

  connection.send("".join(stats_to_send).encode("utf-8"))

#Initialize byte trackers for upload/download speeds
bytes_received = 0
bytes_sent = 0
#tracking packets sent and received for packet loss calculation
packets_sent = 0
packets_recieved = 0

def send_file(connection, file_name):
  """Send a file to the client."""
  file_path = os.path.join(UPLOAD_DIR, file_name)
  if not os.path.exists(file_path):
    connection.send(b'ERROR: File does not exist.')
    return False

  file_size = os.path.getsize(file_path)
  connection.send(f"READY {file_size}".encode())  # Acknowledge readiness to send

  # Send the file in chunks
  with open(file_path, 'rb') as file:
    while chunk := file.read(BUFFER_SIZE):
      connection.send(chunk)
  #connection.send(b'DONE')  # Signal the end of the file transfer
  print(f"[*] File {file_name} sent successfully.")
  return True



def save_file(connection, file_name, file_size):
  #file saved to uploads folder
  received_size = 0
  with open(os.path.join(UPLOAD_DIR, file_name), 'wb') as f:
    while received_size < file_size:
      chunk = connection.recv(min(BUFFER_SIZE, file_size - received_size))
      if not chunk:
        break
      f.write(chunk)
      received_size += len(chunk)
  return received_size


def handle_client(connection, addr):
  #Handle communication with a single client
  global bytes_received, bytes_sent,packets_sent,packets_received

  print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
  print(f'[*] Accepted at {current_client_time(ntp_offset)}')  # Add for timestamps

  try:
    while True:
      # Receive data from client
      data = connection.recv(BUFFER_SIZE)

      # Track bytes received and sent
      bytes_received += len(data)
      bytes_sent += len(data)
      packets_sent = 0
      packets_received = 0
  

      # verify received data
      if not data:
        break
      else:
        try:
          message = data.decode('utf-8').split('||')
          if message[0].startswith("UPLOAD"):
            #start tracking the time for time difference calculation
            start_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
            #split data
            metadata = message[0].split()
            file_name = metadata[1]
            file_size = int(metadata[2])
            file_type = metadata[3]

            #ACK metadata receipt
            connection.send(b'READY')
            packets_sent += 1

          #FILE SAVE LOGIC
          print(f"[*] Receiving {file_name} ({file_type}) of size {file_size} bytes")
          saved_size = save_file(connection, file_name, file_size)
          bytes_received += saved_size #add bytes recieved in file size to tracker for upload speed calcuation
          if saved_size == file_size: #check that enough space is allocated
              print(f"[*] {file_name} received and saved successfully.")
              connection.send(b'File uploaded successfully.')
              #stop the timer for time difference calculation
              end_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
              time_difference = end_time - start_time
              packets_sent += 1
              send_network_stats(connection,bytes_received,bytes_sent,packets_recieved,packets_sent,time_difference)

          else:
              print(f"[!] Error: Received size {saved_size} does not match expected size {file_size}")
              connection.send(b'File upload failed.')
              packets_sent += 1
          
          #FILE DELETE LOGIC
          if message[0].startswith("DELETE"):
            metadata = message[0].split()
            file_name = metadata[1]
            file_path = os.path.join(UPLOAD_DIR, file_name)
            #use os.remove() to delete file from server
            if os.path.exists(file_path):
              os.remove(file_path)
              print(f"[*] File {file_name} deleted successfully.")
              connection.send(f"File {file_name} deleted successfully.".encode())
              packets_sent += 1
            elif message[0].startswith("LIST"):
              try:
                get_dir_content = os.listdir('.')
                response = "\n".join(get_dir_content)
                print(f"[*] preparing directory. {len(get_dir_content)} items in directory.")
                connection.sendall(response.encode())
                connection.sendall(b'END')
                print("[*] Directory listing sent successfully.")
              except Exception as e:
                print(f"[!] Error while listing directory. {e}")
            else: #file doesn't exist so can't be deleted
              print(f"[!] File {file_name} does not exist.")
              connection.send(f"File {file_name} does not exist.".encode())
              packets_sent += 1

          #FILE SEND TIME LOGIC
          else:
            #send time
            client_timestamp_str, client_message = message
            client_timestamp = datetime.strptime(client_timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            server_receive_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
            #subtract send time from receive time
            time_difference = server_receive_time - client_timestamp
            print(f'[*] {server_receive_time} - Data received: {client_message}')
            print(f'[*] Time taken for data to send: {time_difference.total_seconds()} seconds')

          #convert to string
          #print(f'[*] Data received: {}'.format(data.decode('utf-8')))
          connection.send(dashes.encode('utf-8') + data)
          packets_sent +=1 #counts sent packets for packet loss calculation

        except Exception as e:
          print(f"[!] Error processing data: {e}")
          connection.send(b'Error processing data.')
          packets_sent += 1

  except Exception as e:
    print(f"[!] Connection error with {addr}: {e}")
  finally:
    print(f"[*] Connection with {addr} closed.")
    connection.close()


def start_server():
  #Start the multithreaded server
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[*] Server listening on {host}:{port}")

    while True:
      connection, addr = server_socket.accept()
      # Create a new thread for each client connection
      client_thread = threading.Thread(target=handle_client, args=(connection, addr))
      client_thread.start()


if __name__ == "__main__":
  start_server()