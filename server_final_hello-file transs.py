import socket
import threading
import os
import json

def receive_messages(conn):
    while True:
        try:
            header = conn.recv(1024).decode()
            if not header:
                print("[SERVER] Client disconnected.")
                conn.close()
                break
            
            if header.startswith("MSG:"):
                message = header[4:]
                if message.lower() == "bye":
                    print("[CLIENT] ended the chat.")
                    conn.close()
                    break
                print(f"[CLIENT] {message}")
                
            elif header.startswith("FILE:"):
                try:
                    file_info_str = header[5:]
                    file_info = json.loads(file_info_str)
                    filename = file_info["filename"]
                    file_size = file_info["size"]
                    
                    print(f"[SERVER] Receiving file: {filename} ({file_size} bytes)")
                    
                    download_dir = "server_downloads"
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    
                    filepath = os.path.join(download_dir, filename)
                    with open(filepath, 'wb') as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = conn.recv(min(4096, file_size - bytes_received))
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    
                    print(f"[SERVER] File received: {filepath}")
                    conn.send(f"MSG:File {filename} received successfully!".encode())
                    
                except Exception as e:
                    print(f"[SERVER] Error receiving file: {e}")
                    
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            conn.close()
            break

def send_messages(conn):
    while True:
        try:
            user_input = input("[SERVER] You: ")
            
            if user_input.lower() == "bye":
                conn.send("MSG:bye".encode())
                print("[SERVER] You ended the chat.")
                conn.close()
                break
            elif user_input.startswith("/sendfile "):
                filename = user_input[10:].strip()
                
                if os.path.exists(filename):
                    try:
                        file_size = os.path.getsize(filename)
                        file_info = {"filename": os.path.basename(filename), "size": file_size}
                        
                        header = f"FILE:{json.dumps(file_info)}"
                        conn.send(header.encode())
                        
                        print(f"[SERVER] Sending file: {filename} ({file_size} bytes)")
                        
                        with open(filename, 'rb') as f:
                            while True:
                                chunk = f.read(4096)
                                if not chunk:
                                    break
                                conn.send(chunk)
                        
                        print(f"[SERVER] File sent successfully: {filename}")
                        
                    except Exception as e:
                        print(f"[SERVER] Error sending file: {e}")
                        conn.send(f"MSG:Error sending file: {e}".encode())
                else:
                    print(f"[SERVER] File not found: {filename}")
                    conn.send(f"MSG:File not found: {filename}".encode())
            else:
                conn.send(f"MSG:{user_input}".encode())
                
        except Exception as e:
            print(f"[SERVER SEND ERROR] {e}")
            conn.close()
            break

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

# Main server code
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

local_ip = get_local_ip()
port = 12345

server_socket.bind(("0.0.0.0", port))
server_socket.listen(1)

print(f"[SERVER] Server IP: {local_ip}")
print(f"[SERVER] Server Port: {port}")
print(f"[SERVER] Commands: /sendfile <filename>, bye")
print(f"[SERVER] Waiting for client...")

conn, addr = server_socket.accept()
print(f"[SERVER] Connected to {addr}")

conn.send("MSG:Hello from Server! File sharing enabled.".encode())

recv_thread = threading.Thread(target=receive_messages, args=(conn,))
send_thread = threading.Thread(target=send_messages, args=(conn,))
recv_thread.daemon = True
send_thread.daemon = True
recv_thread.start()
send_thread.start()

try:
    recv_thread.join()
    send_thread.join()
except KeyboardInterrupt:
    print("\n[SERVER] Shutting down...")
finally:
    conn.close()
    server_socket.close()
    print("[SERVER] Closed.")
