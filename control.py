import socket

HOST = '10.42.0.138'
PORT = 2107

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print('Connected.')

    while True:
        request = input()
        sock.sendall(request.encode())
        print('Sent: "%s"' % request)
        if request == 'shutdown':
            break
        print('Received: "%s"' % sock.recv(10).decode())

