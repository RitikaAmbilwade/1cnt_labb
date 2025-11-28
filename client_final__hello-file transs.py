import socket
import threading
import os
import json

def receive_messages(client_socket):
    while True:
        try:
            header = client_socket.recv(1024).decode()
            if not header:
                print("[CLIENT] Server disconnected.")
                client_socket.close()
                break
            
            if header.startswith("MSG:"):
                message = header[4:]
                if message.lower() == "bye":
                    print("[SERVER] ended the chat.")
                    client_socket.close()
                    break
                print(f"[SERVER] {message}")
                
            elif header.startswith("FILE:"):
                try:
                    file_info_str = header[5:]
                    file_info = json.loads(file_info_str)
                    filename = file_info["filename"]
                    file_size = file_info["size"]
                    
                    print(f"[CLIENT] Receiving file: {filename} ({file_size} bytes)")
                    
                    download_dir = "client_downloads"
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    
                    filepath = os.path.join(download_dir, filename)
                    with open(filepath, 'wb') as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = client_socket.recv(min(4096, file_size - bytes_received))
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    
                    print(f"[CLIENT] File received: {filepath}")
                    client_socket.send(f"MSG:File {filename} received successfully!".encode())
                    
                except Exception as e:
                    print(f"[CLIENT] Error receiving file: {e}")
                    
        except Exception as e:
            print(f"[CLIENT ERROR] {e}")
            client_socket.close()
            break

def send_messages(client_socket):
    while True:
        try:
            user_input = input("[CLIENT] You: ")
            
            if user_input.lower() == "bye":
                client_socket.send("MSG:bye".encode())
                print("[CLIENT] You ended the chat.")
                client_socket.close()
                break
            elif user_input.startswith("/sendfile "):
                filename = user_input[10:].strip()
                
                if os.path.exists(filename):
                    try:
                        file_size = os.path.getsize(filename)
                        file_info = {"filename": os.path.basename(filename), "size": file_size}
                        
                        header = f"FILE:{json.dumps(file_info)}"
                        client_socket.send(header.encode())
                        
                        print(f"[CLIENT] Sending file: {filename} ({file_size} bytes)")
                        
                        with open(filename, 'rb') as f:
                            while True:
                                chunk = f.read(4096)
                                if not chunk:
                                    break
                                client_socket.send(chunk)
                        
                        print(f"[CLIENT] File sent successfully: {filename}")
                        
                    except Exception as e:
                        print(f"[CLIENT] Error sending file: {e}")
                        client_socket.send(f"MSG:Error sending file: {e}".encode())
                else:
                    print(f"[CLIENT] File not found: {filename}")
                    client_socket.send(f"MSG:File not found: {filename}".encode())
            else:
                client_socket.send(f"MSG:{user_input}".encode())
                
        except Exception as e:
            print(f"[CLIENT SEND ERROR] {e}")
            client_socket.close()
            break

# Main client code
print("=== TCP Client with Chat & File Sharing ===")
server_ip = input("Enter server IP address: ").strip()
if not server_ip:
    server_ip = "localhost"

port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print(f"[CLIENT] Connecting to {server_ip}:{port}...")
    client_socket.connect((server_ip, port))
    print("[CLIENT] Connected!")
    print("[CLIENT] Commands: /sendfile <filename>, bye")
    
    client_socket.send("MSG:Hello from Client! Ready for chat and files.".encode())
    
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    
    recv_thread.daemon = True
    send_thread.daemon = True
    
    recv_thread.start()
    send_thread.start()
    
    try:
        recv_thread.join()
        send_thread.join()
    except KeyboardInterrupt:
        print("\n[CLIENT] Shutting down...")
    
except ConnectionRefusedError:
    print(f"[CLIENT] Could not connect to {server_ip}:{port}")
except Exception as e:
    print(f"[CLIENT ERROR] {e}")
finally:
    client_socket.close()
    print("[CLIENT] Closed.")
