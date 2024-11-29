import socket
import os
import time

class FileShareClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.send_dir = os.path.join(self.script_dir, 'files_to_send')
        self.download_dir = os.path.join(self.script_dir, 'downloads')

        # Create necessary directories
        os.makedirs(self.send_dir, exist_ok=True)
        os.makedirs(self.download_dir, exist_ok=True)

    def send_file(self, filename):
        # Construct full file path
        filepath = os.path.join(self.send_dir, filename)
        
        # Validate file exists
        if not os.path.exists(filepath):
            print(f"[!] File {filename} not found")
            return False
        
        # Get file size
        filesize = os.path.getsize(filepath)
        
        # Create client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        
        try:
            # Send operation type (upload)
            client_socket.send(b'UPLOAD')
            time.sleep(0.1)  # Small delay to ensure server processes
            
            # Send filename with fixed-length padding
            filename_bytes = filename.encode('utf-8')
            filename_length = len(filename_bytes)
            client_socket.send(f"{filename_length:10}".encode('utf-8'))
            client_socket.send(filename_bytes)
            
            # Send filesize with fixed-length padding
            client_socket.send(f"{filesize:20}".encode('utf-8'))
            
            # Send file contents
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.send(data)
            
            print(f"[✓] File {filename} sent successfully")
            return True
        
        except Exception as e:
            print(f"[!] Error sending file: {e}")
            return False
        
        finally:
            client_socket.close()

    def download_file(self, filename):
        # Create client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        
        try:
            # Send operation type (download)
            client_socket.send(b'DOWNLOAD')
            time.sleep(0.1)  # Small delay to ensure server processes
            
            # Send filename with fixed-length padding
            filename_bytes = filename.encode('utf-8')
            filename_length = len(filename_bytes)
            client_socket.send(f"{filename_length:10}".encode('utf-8'))
            client_socket.send(filename_bytes)
            
            # Receive filesize
            filesize_bytes = client_socket.recv(20).decode('utf-8').strip()
            filesize = int(filesize_bytes)
            
            # Prepare to receive file
            filepath = os.path.join(self.download_dir, filename)
            
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
            
            print(f"[✓] File {filename} downloaded successfully")
            print(f"   Saved to: {filepath}")
            return True
        
        except Exception as e:
            print(f"[!] Error downloading file: {e}")
            return False
        
        finally:
            client_socket.close()

    def main(self):
        print("File Sharing Client")
        print("1. Upload File")
        print("2. Download File")
        
        choice = input("Enter your choice (1/2): ").strip()
        
        if choice == '1':
            # List uploadable files
            available_files = os.listdir(self.send_dir)
            if not available_files:
                print("[!] No files found in files_to_send directory")
                return
            
            print("Available files:", available_files)
            filename = input("Enter filename to upload: ").strip()
            
            if filename not in available_files:
                print(f"[!] File '{filename}' not found")
                return
            
            self.send_file(filename)
        
        elif choice == '2':
            filename = input("Enter filename to download: ").strip()
            self.download_file(filename)
        
        else:
            print("[!] Invalid choice")

if __name__ == "__main__":
    client = FileShareClient()
    client.main()