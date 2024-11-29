import socket
import os

def start_server(host='127.0.0.1', port=65432):
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print(f"[*] Server listening on {host}:{port}")
    
    while True:
        try:
            # Accept client connection
            client_socket, address = server_socket.accept()
            print(f"[+] Connection from {address}")
            
            try:
                # Receive filename length
                filename_length_bytes = client_socket.recv(10).decode('utf-8').strip()
                filename_length = int(filename_length_bytes)
                
                # Receive filename
                filename = client_socket.recv(filename_length).decode('utf-8')
                
                # Receive filesize
                filesize_bytes = client_socket.recv(20).decode('utf-8').strip()
                filesize = int(filesize_bytes)
                
                # Ensure received files directory exists
                os.makedirs('received_files', exist_ok=True)
                
                # Prepare to receive file
                filepath = os.path.join('received_files', filename)
                
                # Receive file
                with open(filepath, 'wb') as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        # Calculate remaining bytes
                        remaining = filesize - bytes_received
                        chunk_size = min(1024, remaining)
                        
                        data = client_socket.recv(chunk_size)
                        if not data:
                            print("[!] Connection interrupted")
                            break
                        
                        f.write(data)
                        bytes_received += len(data)
                
                print(f"[✓] File {filename} received successfully")
                print(f"   Size: {bytes_received} bytes")
            
            except Exception as e:
                print(f"[!] Error receiving file: {e}")
            
            finally:
                client_socket.close()
        
        except KeyboardInterrupt:
            print("\n[*] Server shutting down")
            break
        except Exception as e:
            print(f"[!] Server error: {e}")

if __name__ == "__main__":
    start_server()