import socket
import os

def send_file(filename, host='127.0.0.1', port=65432):
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the file
    filepath = os.path.join(script_dir, 'files_to_send', filename)
    
    # Validate file exists
    if not os.path.exists(filepath):
        print(f"[!] File {filename} not found")
        return
    
    # Get file size
    filesize = os.path.getsize(filepath)
    
    # Create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    try:
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
    
    except Exception as e:
        print(f"[!] Error sending file: {e}")
    
    finally:
        client_socket.close()

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(script_dir, 'files_to_send')
    
    print("File Sharing Client")
    
    # Ensure files_to_send directory exists
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
        print(f"[!] Created files_to_send directory at: {files_dir}")
    
    # List available files
    available_files = os.listdir(files_dir)
    
    if not available_files:
        print("[!] No files found in files_to_send directory")
        print(f"Please add files to: {files_dir}")
        return
    
    print("Available files:", available_files)
    
    while True:
        filename = input("Enter filename to send: ").strip()
        if not filename:
            print("[!] Please enter a valid filename")
            continue
        
        if filename not in available_files:
            print(f"[!] File '{filename}' not found in files_to_send directory")
            continue
        
        send_file(filename)
        break

if __name__ == "__main__":
    main()