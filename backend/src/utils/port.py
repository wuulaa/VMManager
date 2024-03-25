import socket

def find_first_available_port(remote_ip, start_port=6000, max_attempts=100):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((remote_ip, port))
                return port
            except socket.error as e:
                if e.errno == socket.errno.EADDRINUSE:
                    continue
                else:
                    raise
    raise RuntimeError("Unable to find an available port.")


def is_port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((ip, port))
            return False
        except:
            return True