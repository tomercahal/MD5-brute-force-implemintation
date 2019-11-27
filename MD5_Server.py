from hashlib import md5
import socket
import time
import threading
import multiprocessing
import os
import sys
#############################################  ANSWER IS: 3735928559 ###################################################
ALL_SOCKETS_IN_USE = 'All sockets are being used at the time please wait'  # Used when all there are 10 users logged


class Server (object):
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 220  # The chose port to have the connection on
        self.HASH = 'EC9C0F7EDCC18A98B1F31853B181330'  # This is the hash that we need to match (the answer md5d)
        self.START_NUM = 3735928259  # The number that the hash starts with
        self.FINISH_NUM = 9999999999  # The number that the hash ends with
        self.CHOSEN_RANGE = 10000  # This is the range that the client will go over each time
        self.HASH_FOUND = 'The hash has been found! it is: '  # Just a simple message it will be used later
        self.found = False  # This will change if the hash has been 5 (some client found the md5)
        self.active_users = []  # This is a list containing the threads that are active and if there are any open
        self.users_allowed = sys.maxint   # This is the amount of users that are allowed to be logged in at the same time
        self.sem = threading.Semaphore(self.users_allowed)  # users allowed is a variable making the program dynamic

    def connect_client(self, client_sock):
        """This function knows how to handle many clients coming in, it let's a user know if all the sockets are full
        and he has to wait. It returns the thread number that it will be assigned later."""
        connection_available = True
        printed_once = False
        while connection_available:  # used so
            for user in range(self.users_allowed):
                if self.active_users[user] == 0:
                    self.active_users[user] = self.active_users.index(0) + 1
                    return self.active_users[user]  # We have found a number that can be assigned to the thread
            if not printed_once:  # If we have not send a reply to the user yet
                print ALL_SOCKETS_IN_USE
                client_sock.send(ALL_SOCKETS_IN_USE)
                printed_once = True  # Now the user won't get the message anymore

    def handle_thread(self, client_sock, thread_num):
        """ This function handles the clients. Since only users_allowed (10 at the time), can be connected and send
        requests at a time."""
        print 'You are thread number: ' + str(thread_num)
        self.sem.acquire()  # Decreases the users logged in at the time (new thread opened)
        print 'New client connected to the database + ' + str(self.sem._Semaphore__value) + ' sockets left\r\n'
        self.send_to_client(client_sock)

    def start(self):
        """Another main function in the server side, It is mainly used to aceept new clients through creating sockets
        and then directing the code to assaign them their jobs to find."""
        try:
            # check_sockets_active(active_users)  # change if got time to make sure every number is ran

            print('Server starting up on ip %s port %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.IP, self.PORT))
            sock.listen(1)
            thread_number = 0  # This will be sort of an ID for the thread, used in debugging
            while True:  # Keep accepting as many people that want to help (speed up the process)
                thread_number += 1  # Increasing cause of new client
                print('\r\nWaiting for a new client')
                client_socket, client_address = sock.accept()  # Last step of being on a socket
                print('New client entered!')
                client_socket.sendall('Hello this is server'.encode())
                thread = threading.Thread(target=self.handle_thread, args=(client_socket, thread_number))
                thread.start()  # Starting the thread

        except socket.error as e:
            print(e)

    def send_to_client(self, client_socket):
        """In this function I will send the client the job he has do to(basically his part) in
         finding the 10 digit number.
         The format of the data will be: [hash code wanted]/start of job/end of job"""
        while not self.found and self.START_NUM < self.FINISH_NUM:  # While no client found the md5 hash value or max num
            data_to_send = "%s/%s/%s" % (self.HASH.lower(), self.START_NUM, self.START_NUM + self.CHOSEN_RANGE)
            print 'Sending to the client: ' + data_to_send  # The data that is sent to the client
            client_socket.send(data_to_send)  # Send to the client the range he needs to check
            self.receive_from_client(client_socket)
            self.START_NUM += self.CHOSEN_RANGE  # Increasing the global variable until we get to finish num.
        client_socket.send('Thank you for helping us find the number we were looking for! Cheers!')
        self.sem.release()  # Releasing the client, no longer need him.

    def receive_from_client(self, client_socket):
        """In this function I will receive the status of the completed job from the client. He will send me
        back the status of the job using this format: [Bool]/None or the number if found"""
        response = client_socket.recv(1024)  # Getting the response from the user.
        parts = response.split('/')  # Splitting the user's answer.
        print 'this is parts: it is a list ' + str(parts)
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
