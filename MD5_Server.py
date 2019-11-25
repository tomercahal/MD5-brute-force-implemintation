from hashlib import md5
import socket
import time
import threading
import multiprocessing
import os

#############################################  ANSWER IS: 3735928559 ###################################################


class Server (object):
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 220  # The chose port to have the connection on
        self.HASH = 'EC9C0F7EDCC18A98B1F31853B181330'  # This is the hash that we need to match
        self.OPEN_SOCKETS = []  # A list of all the sockets that are currently in use and open.
        self.START_NUM = 1000000000  # The number that the hash starts with
        self.FINISH_NUM = 9999999999  # The number that the hash ends with
        self.CHOSEN_RANGE = 10000  # This is the range that the client will go over each time
        self.HASH_FOUND = 'The hash has been found! it is: '  # Just a simple message it will be used later

    def start(self):
        """Another main function in the server side, It is mainly used to aceept new clients through creating sockets
        and then directing the code to assaign them their jobs to find."""
        try:
            # check_sockets_active(OPEN_SOCKETS)  # change if got time to make sure every number is ran

            print('Server starting up on ip %s port %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.IP, self.PORT))
            sock.listen(1)
            while True:
                print('Waiting for a new client')
                client_socket, client_address = sock.accept()  # Last step of being on a socket
                print('New client entered!')
                client_socket.sendall('Hello this is server'.encode())
                self.OPEN_SOCKETS.append(client_socket)  # Adding the new socket to the list
                msg = client_socket.recv(1024)
                print('Received message: %s' % msg.decode())
                for s in self.OPEN_SOCKETS:
                    thread_each_socket = threading.Thread(target=self.handle_client, args=(s,))  # Creating a thread
                    thread_each_socket.start()

        except socket.error as e:
            print(e)

    def handle_client(self, client_socket):
        """This function is the main function that calls all the other ones. It is sort of like the manager. From here
        we will send a new range to the clients and get their calculations to see it they have the match. If they don't
        we will send them a new set of numbers, till we don't have anymore left."""
        while self.START_NUM < self.FINISH_NUM:
            thread = threading.Thread(target=self.send_to_client, args=(client_socket,))  # Creating the thread
            thread.start()  # activating the thread and now it goes to send_to_client func
            thread_recv = threading.Thread(target=self.receive_from_client, args=(client_socket,))  # The receiving thread, gets input from client
            thread_recv.start()
            thread_recv.join()  # waiting for the receiving thread, cause we must get an answer if it was in the range.
            self.START_NUM += self.CHOSEN_RANGE  # increasing the global variable until we get to finish num.

    def send_to_client(self, client_socket):
        """In this function I will send the client the job he has do to(basically his part) in
         finding the 10 digit number.
         The format of the data will be: [hash code wanted]/start of job/end of job"""
        data_to_send = "%s/%s/%s" % (self.HASH.lower(), self.START_NUM, self.START_NUM + self.CHOSEN_RANGE)
        print 'Sending to the client: ' + data_to_send  # The data that is sent to the client
        client_socket.sendall(data_to_send)

    def receive_from_client(self, client_socket):
        """In this function I will receive the status of the completed job from the client. He will send me
        back the status of the job using this format: [Bool]/None or the number if found"""
        response = client_socket.recv(1024)
        parts = response.split('/')
        print parts
        bool_found = parts[0]
        print parts[0], 'num is: ' + parts[1]
        if not bool_found:  # if the number is found WEIRDD
            print self.HASH_FOUND + parts[1]
            os._exit(0)  # Terminates the current program since the number has been found
        else:
            return


if __name__ == '__main__':
    s = Server()
    s.start()