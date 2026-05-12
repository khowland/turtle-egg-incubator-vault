import socket
import errno

def scan_ports(host='127.0.0.1', start=1, end=1000):
    for port in range(start, end + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            print(f"Port {port} is OPEN")
        except socket.error:
            pass
        finally:
            s.close()

if __name__ == "__main__":
    print("Scanning 127.0.0.1...")
    scan_ports('127.0.0.1', 1, 1000)
    print("Scanning 0.0.0.0...")
    scan_ports('0.0.0.0', 1, 1000)
