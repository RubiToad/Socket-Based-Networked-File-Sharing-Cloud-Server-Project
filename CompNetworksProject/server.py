import socket
from network_analysis import *  # add for timestamps
host = '10.162.0.2'
port = 3300
BUFFER_SIZE = 1024
dashes = '----> '
ntp_offset = get_time_offset()  # add for timestamps

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_tcp:
  server_tcp.bind((host, port))

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

<<<<<<< Updated upstream
        #convert to string
        #print('[*] Data received: {}'.format(data.decode('utf-8')))
        connection.send(dashes.encode('utf-8') + data)
=======
            #FILE SAVE LOGIC
            print(f"[*] Receiving {file_name} ({file_type}) of size {file_size} bytes")
            saved_size = save_file(connection, file_name, file_size)
            if saved_size == file_size: #check that enough space is allocated?
              print(f"[*] {file_name} received and saved successfully.")
              connection.send(b'File uploaded successfully.')
            else:
              print(f"[!] Error: Received size {saved_size} does not match expected size {file_size}")
              connection.send(b'File upload failed.')
            #FILE DELETE LOGIC
          elif message[0].startswith("DELETE"):
            metadata = message[0].split()
            file_name = metadata[1]
            file_path = os.path.join(UPLOAD_DIR, file_name)
            #use os.remove() to delete file from server
            if os.path.exists(file_path):
              os.remove(file_path)
              print(f"[*] File {file_name} deleted successfully.")
              connection.send(f"File {file_name} deleted successfully.".encode())
            else: #file doesn't exist so can't be deleted
              print(f"[!] File {file_name} does not exist.")
              connection.send(f"File {file_name} does not exist.".encode())

          #FILE SEND TIME LOGIC
          else:
            #send time
            client_timestamp_str, client_message = message
            client_timestamp = datetime.strptime(client_timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            server_receive_time = datetime.now() + timedelta(seconds=ntp_offset)

            #subtract send time from receive time
            time_difference = server_receive_time - client_timestamp
            print(f'[*] {server_receive_time} - Data received: {client_message}')
            print(f'[*] Time taken for data to send: {time_difference.total_seconds()} seconds')

            #convert to string
            #print('[*] Data received: {}'.format(data.decode('utf-8')))
            connection.send(dashes.encode('utf-8') + data)
        except Exception as e:
          print(f"[!] Error processing data: {e}")
          connection.send(b'Error processing data.')
>>>>>>> Stashed changes
