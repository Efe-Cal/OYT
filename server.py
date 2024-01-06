import socket
import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8888))
server_socket.listen(5)

sockets_list = [server_socket]
clients = {}

while True:
    read_sockets, _, _ = select.select(sockets_list, [], [])

    for sock in read_sockets:
        if sock == server_socket:
            client_socket, client_address = server_socket.accept()
            sockets_list.append(client_socket)
            clients[client_socket] = client_address
            print(f"Accepted connection from {client_address}")

        else:
            data = sock.recv(1024).decode('utf-8')
            if data:
                splitedData = data.split("\n")
                host = splitedData[0]
                sinifin_tum_ogrencileri = list(map(lambda x:x.split(":"),splitedData[1:])) # -> [['Ahmet MAHMUT', '12.00'], ['Mehmet MAHMUT', '12.00']]
                sinifin_tum_ogrencileri[0] # -> ['Ahmet MAHMUT', '12.00']
                sinifin_tum_ogrencileri[0][0] # -> 'Ahmet MAHMUT'
                print(sinifin_tum_ogrencileri)

            else:
                print(f"Closed connection from {clients[sock]}")
                sockets_list.remove(sock)
                del clients[sock]
                sock.close()