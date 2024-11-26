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
  """Handle communication with a single client."""
  global bytes_received, bytes_sent, packets_sent, packets_received

  print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
  print(f'[*] Accepted at {current_client_time(ntp_offset)}')  # Add for timestamps

  try:
    while True:
      # Receive data from client
      data = connection.recv(BUFFER_SIZE)
      if not data:
        break

      # Decode data for processing and split into parts
      message = data.decode('utf-8').split('||')  # Split into command and additional data

      try:
        # Use message[0] (command) for all checks
        if message[0].startswith("UPLOAD"):
          # start tracking the time for time difference calculation
          start_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
          metadata = message[0].split()
          file_name = metadata[1]
          file_size = int(metadata[2])
          file_type = metadata[3]

          connection.send(b'READY')

          print(f"[*] Receiving {file_name} ({file_type}) of size {file_size} bytes")
          saved_size = save_file(connection, file_name, file_size)
          bytes_received += saved_size  # add bytes recieved in file size to tracker for upload speed calcuation
          if saved_size == file_size:
            print(f"[*] {file_name} received and saved successfully.")
            connection.send(b'File uploaded successfully.')
            # stop the timer for time difference calculation
            end_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
            time_difference = end_time - start_time
            packets_sent += 1
            send_network_stats(connection, bytes_received, bytes_sent, packets_recieved, packets_sent, time_difference)
          else:
            connection.send(b'File upload failed.')

        elif message[0].startswith("DELETE"):
          file_name = message[0].split(" ", 1)[1].strip()
          file_path = os.path.join(UPLOAD_DIR, file_name)
          if os.path.exists(file_path):
            os.remove(file_path)
            connection.send(f"File '{file_name}' deleted successfully.".encode('utf-8'))
          else:
            connection.send(f"File '{file_name}' does not exist.".encode('utf-8'))

        elif message[0].startswith("SUBFOLDER CREATE"):
          folder_path = message[0].split(" ", 2)[2].strip()
          full_path = os.path.join(UPLOAD_DIR, folder_path)
          try:
            os.makedirs(full_path, exist_ok=True)
            connection.send(f"Subfolder '{folder_path}' created successfully.".encode('utf-8'))
          except Exception as e:
            connection.send(f"Error creating subfolder: {e}".encode('utf-8'))

        elif message[0].startswith("SUBFOLDER DELETE"):
          folder_path = message[0].split(" ", 2)[2].strip()
          full_path = os.path.join(UPLOAD_DIR, folder_path)
          try:
            if os.path.exists(full_path):
              os.rmdir(full_path)
              connection.send(f"Subfolder '{folder_path}' deleted successfully.".encode('utf-8'))
            else:
              connection.send(f"Subfolder '{folder_path}' does not exist.".encode('utf-8'))
          except Exception as e:
            connection.send(f"Error deleting subfolder: {e}".encode('utf-8'))

        elif message[0].startswith("LIST"):
          try:
            dir_content = os.listdir('.')
            response = "\n".join(dir_content)
            connection.sendall(response.encode())
            connection.sendall(b'END')
          except Exception as e:
            connection.send(f"Error listing directory: {e}".encode())

        elif message[0].startswith("DOWNLOAD"):
          file_name = message[0].split(" ", 1)[1]
          if send_file(connection, file_name):
            print(f"[*] File {file_name} sent successfully.")

        else:
          connection.send("Unknown command received.".encode('utf-8'))

      except Exception as e:
        print(f"[!] Error processing data: {e}")
        connection.send(b'Error processing data.')

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