import socket
import os

class FileShareServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.server_files_dir = 'server_files'
        
        
        os.makedirs(self.server_files_dir, exist_ok=True)

    def start_server(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"[*] Server listening on {self.host}:{self.port}")
        
        while True:
            try:
        
                client_socket, address = server_socket.accept()
                print(f"[+] Connection from {address}")
                
                try:
                    
                    operation = client_socket.recv(10).decode('utf-8').strip()
                    
                    
                    filename_length_bytes = client_socket.recv(10).decode('utf-8').strip()
                    filename_length = int(filename_length_bytes)
                    
                    
                    filename = client_socket.recv(filename_length).decode('utf-8')
                    
                    if operation == 'UPLOAD':
                        self.handle_upload(client_socket, filename)
                    elif operation == 'DOWNLOAD':
                        self.handle_download(client_socket, filename)
                
                except Exception as e:
                    print(f"[!] Error processing request: {e}")
                
                finally:
                    client_socket.close()
            
            except KeyboardInterrupt:
                print("\n[*] Server shutting down")
                break
            except Exception as e:
                print(f"[!] Server error: {e}")

    def handle_upload(self, client_socket, filename):

        filesize_bytes = client_socket.recv(20).decode('utf-8').strip()
        filesize = int(filesize_bytes)
        
        
        filepath = os.path.join(self.server_files_dir, filename)
        
        
        with open(filepath, 'wb') as f:
            bytes_received = 0
            while bytes_received < filesize:
                
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

    def handle_download(self, client_socket, filename):
        
        filepath = os.path.join(self.server_files_dir, filename)
        
        
        if not os.path.exists(filepath):
            print(f"[!] File {filename} not found")
            client_socket.send(b'0' * 20) 
        
        
        filesize = os.path.getsize(filepath)
        
        
        client_socket.send(f"{filesize:20}".encode('utf-8'))
    
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)
        
        print(f"[✓] File {filename} sent successfully")

if __name__ == "__main__":
    server = FileShareServer()
    server.start_server()