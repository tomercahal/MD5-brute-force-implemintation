import socket
import threading
import multiprocessing
import sys

#############################################  ANSWER IS: 3735928559 ###################################################
ALL_SOCKETS_IN_USE = 'All sockets are being used at the time please wait'  # Used when all there are 10 users logged


def write_or_create_text_file(data):
    """This function creates a text file on the client's computer"""
    with open('Server found number.txt', 'w') as f:
        if data == 'create':  # In the first time we need to create a text file
            f.write('False')  # Start it up as False
        else:
            f.write(data)


def check_if_found():
    """Since multiprocessing creates an entirely new instance of python, I need a way to share a variable between
     my threads. I chose to make a text file and write in it,
     this function checks if the number has been found already"""
    with open('server found number.txt', 'r') as f:
        data = f.read()
        return data


class Server (object):  # The server's class
    def __init__(self):
        """The constructor of the Server"""
        self.IP = '127.0.0.1'  # The IP of the server.
        self.PORT = 220  # The chose port to have the connection on
        self.HASH = 'EC9C0F7EDCC18A98B1F31853B1813301'  # This is the hash that we need to match (the answer md5d)
        self.START_NUM = 3735508558  # The number that the hash starts with, setting it up close so won't take so long
        self.FINISH_NUM = 9999999999  # The number that the hash ends with
        self.CHOSEN_RANGE = 10000  # This is the range that the client will go over each time
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

    def handle_thread(self, client_sock, thread_num, que):
        """ This function handles the clients. Since only users_allowed (10 at the time), can be connected and send
        requests at a time."""
        print 'You are thread number: ' + str(thread_num)
        self.sem.acquire()  # Decreases the users logged in at the time (new thread opened)
        print 'New client connected to the database + ' + str(self.sem._Semaphore__value) + ' sockets left\r\n'
        self.send_to_client(client_sock, thread_num, que)

    def start(self):
        """Another main function in the server side, It is mainly used to aceept new clients through creating sockets
        and then directing the code to assaign them their jobs to find."""
        try:
            # check_sockets_active(active_users)  # change if got time to make sure every number is ran

            print('Server starting up on ip %s port %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            print '\r\nToday we are looking for this MD5 hash: ' + self.HASH + '\r\nHopefully we can find it!'
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.IP, self.PORT))
            sock.listen(1)
            thread_number = 0  # This will be sort of an ID for the thread, used in debugging
            write_or_create_text_file('create')   # Creates the text file in the server's directory
            que = multiprocessing.Queue()  # Creating a que that the threads will use
            que.put(self.START_NUM)  # Inserting the value of the number into a queue
            while True:  # Keep accepting as many people that want to help (speed up the process)
                thread_number += 1  # Increasing cause of new client
                print('\r\nWaiting for a new client')
                client_socket, client_address = sock.accept()  # Last step of being on a socket
                print('New client entered!')
                client_socket.sendall('Hello this is Tomer\'s server, thank you for helping me today!'.encode())
                thread = threading.Thread(target=self.handle_thread, args=(client_socket, thread_number, que))
                thread.start()  # Starting the thread

        except socket.error as e:
            print(e)

    def send_to_client(self, client_socket, thread_num, que):
        """In this function I will send the client the job he has do to(basically his part) in
         finding the 10 digit number.
         The format of the data will be: [hash code wanted]/start of job/end of job"""
        found = check_if_found()  # This checks if one of the clients has found the number
        start_num = que.get()  # The updated start num, from other processes etc
        while not found == 'True' and start_num < self.FINISH_NUM:  # While no client found the md5 hash value or max num
            que.put(start_num + self.CHOSEN_RANGE)  # Updating start num
            data_to_send = "%s/%s/%s" % (self.HASH.lower(), start_num, start_num + self.CHOSEN_RANGE)
            print 'Sending to client ' + str(thread_num) + ': ' + data_to_send  # The data that is sent to the client
            client_socket.send(data_to_send)  # Send to the client the range he needs to check
            self.receive_from_client(client_socket)
            found = check_if_found()  # This checks if one of the clients has found the number
            if found == 'True':
                break
            start_num = que.get()  # The updated start num, from other processes etc
        if found:
            client_socket.send('Thank you for helping us find the number we were looking for! Cheers!')
        else:
            client_socket.send('Unfortunately, the md5 hash we were looking for has not been found,'
                               ' but thank you for helping!')
        self.sem.release()  # Releasing the client, no longer need him.

    def receive_from_client(self, client_socket):
        """In this function I will receive the status of the completed job from the client. He will send me
        back the status of the job using this format: [Bool]/None or the number if found"""
        response = client_socket.recv(1024)  # Getting the response from the user.
        parts = response.split('/')  # Splitting the user's answer.
        bool_found = parts[0]
        print 'Did the user find the number? ' + parts[0], 'num is: ' + parts[1]  # parts[0] is True or False, parts[1] is the number or None
        if bool_found == 'True':  # If the number has been found
            write_or_create_text_file('True')
            print 'The number has been found!!!!! It is: ' + parts[1]
        else:
            print 'Number has not been found yet I will keep searching!\r\n'  # Just a quick update for every run


if __name__ == '__main__':
    s = Server()  # Creating a new server object
    s.start()  # Starting the server
