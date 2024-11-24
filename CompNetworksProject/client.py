import socket
import os
from datetime import datetime, timedelta

from network_analysis import *
import requests




host = '34.174.190.227'
port = 3300



BUFFER_SIZE = 25 * 1024 * 1024
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


def upload_file(file_path):
  # Function to upload a file (text, image, or audio) to the server.
  if not os.path.exists(file_path):
    print(f"File {file_path} does not exist.")
    return

  file_name = os.path.basename(file_path)
  file_size = os.path.getsize(file_path)

  # Determine the file type based on its extension
  file_type = 'text'
  if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
    file_type = 'image'
  elif file_path.lower().endswith(('.mp3', '.wav', '.aac')):
    file_type = 'audio'

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
    client_tcp.connect((host, port))

    # Get the current timestamp and format it
    client_send_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
    client_send_time_str = client_send_time.strftime('%Y-%m-%d %H:%M:%S.%f')

    # Prepare the metadata to send to the server
    metadata = f"UPLOAD {file_name} {file_size} {file_type}||{client_send_time_str}"
    client_tcp.send(metadata.encode())

    # Wait for server acknowledgment
    ack = client_tcp.recv(BUFFER_SIZE).decode()
    if ack != 'READY':
      print("Server not ready for upload.")
      return

    # Upload the file in chunks
    print(f"Uploading {file_name}...")
    with open(file_path, 'rb') as file:
      while True:
        chunk = file.read(BUFFER_SIZE)
        if not chunk:
          break
        client_tcp.send(chunk)

    print(f"{file_name} uploaded successfully.")
    client_tcp.send(b'DONE')

    # Receive server response and print speeds
    response = client_tcp.recv(BUFFER_SIZE).decode()
    print(f"The message received from the server: {response}")
    print(f"The upload speed was: {get_upload_speed()} MB/s")
    print(f"The download speed was: {get_download_speed()} MB/s")

def delete_file(file_name):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
    client_tcp.connect((host, port))

    #delete request
    client_send_time = datetime.utcnow() + timedelta(seconds=ntp_offset)
    client_send_time_str = client_send_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    metadata = f"DELETE {file_name}||{client_send_time_str}"
    client_tcp.send(metadata.encode())
    response = client_tcp.recv(BUFFER_SIZE).decode()
    print(f"Server response: {response}")

def display_menu():
  # Display a basic UI for interacting with the client.
  print("\n--- File Sharing Client ---")
  print("1. Upload a File")
  print("2. Send a Message")
  print("3. Delete a File")
  print("4. Download a File")
  print("5. Exit")

def download_file(file_name):
    """Request a file from the server and save it locally."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((host, port))

        # Send a DOWNLOAD command with the file name
        metadata = f"DOWNLOAD {file_name}||"
        client_tcp.send(metadata.encode())

        # Wait for the server's acknowledgment
        ack = client_tcp.recv(BUFFER_SIZE).decode()
        if ack != "READY":
            print(f"Error: {ack}")
            return

        # Start receiving the file
        print(f"Downloading file: {file_name}...")
        file_path = os.path.join(os.getcwd(), file_name)  # Save in the current directory
        with open(file_path, 'wb') as file:
            while True:
                chunk = client_tcp.recv(BUFFER_SIZE)
                if chunk == b'DONE':  # End of file signal
                    break
                if not chunk:
                    print("[!] Connection lost.")
                    return
                file.write(chunk)

        print(f"File {file_name} downloaded successfully to {file_path}.")

if __name__ == '__main__':
  while True:
    display_menu()
    choice = input("Enter your choice: ")

    if choice == '1':
      file_path = input("Enter the path of the file to upload: ")
      upload_file(file_path)
    elif choice == '2':
      message = input("Enter a message or 'q' to quit: ")
      if message == 'q':
        quit()
      else:
        next(setup_connection(message))
    elif choice == '3':
      deleted_file = input("Enter the name of the file you want to delete: ")
      delete_file(deleted_file)
    elif choice == '4':
      file_name=input("Enter the name of the file you want to download: ")
      download_file(file_name)

    elif choice == '5':
      print("Exiting...")
      break
    else:
      print("Invalid choice. Please try again.")
