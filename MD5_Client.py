import socket
import time
import multiprocessing
import hashlib
import time
import os


#############################################  ANSWER IS: 3735928559 ###################################################

def check_hash(num):
    """This function gets a number as the input and returns the hash code of the number that was the input."""
    hashAlgo = hashlib.md5()
    pw = str(num)
    hashAlgo.update(pw.encode('utf-8'))
    hash = hashAlgo.hexdigest()
    return hash


class Client (object):
    def __init__(self):
        """The constructor of the Client class"""
        self.IP = '127.0.0.1'  # The Ip of the client.
        self.PORT = 220  # The port of the client.
        self.cores = 0  # A variable that contains the amount of cores the pc has
        self.processes_running = []  # A list of all the processes running at the time
        self.found = False

    def start(self):
        """Sort of like the main function, it binds a socket connection to the server and gets the jobs that he asks."""
        try:
            print('connecting to IP %s PORT %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            global sock
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.IP, self.PORT))

            print('connected to server')
            msg = sock.recv(1024)
            print('received message: %s' % msg.decode())
            self.cores = multiprocessing.cpu_count()
            print "The amount of cores this client has is: " + str(self.cores)
            self.handle_server_job(sock)

        except socket.error as e:
            print(e)
            sock.close()

    def run_over_range(self, start_num, end_num, hash_needed, que):
        """This function is called on each process and it goes over the range of the numbers that
         the process needs to go over"""
        while not self.found and start_num != end_num:  # If number not found yet or start num isn't equal to end num
            hash_of_num = check_hash(start_num)
            if hash_of_num == hash_needed:
                print 'number found!'
                que.put(start_num)  # inserting the value of the number into a queue
                self.found = True
                break
            start_num += 1

    def handle_server_job(self, server_socket):
        print 'im in handle server job'
        while not self.found:
            job = sock.recv(1024)  # Getting the range and hash from the server
            print 'The job is: ' + str(job)
            parts_of_job = job.split('/')  # This splits according to the the protocol the server transfers the details.
            print parts_of_job
            OG_HASH = parts_of_job[0]  # The hash that we will need to compare to.
            start_num = int(parts_of_job[1])
            finish_num = int(parts_of_job[2])
            each_core_work = 1 + ((finish_num-start_num)/self.cores) # how many numbers will each core(process) go over in order to be efficient.
            print start_num, finish_num, each_core_work
            que = multiprocessing.Queue()
            p = ''
            for i in range(self.cores):
                print 'Started process number: ' + str(i+1)  # Adding 1 so it would not start from 0
                print 'These are the args:\r\n' + str(start_num + (i * each_core_work)), \
                    str(start_num + ((i+1) * each_core_work)), OG_HASH, que, self.found
                p = multiprocessing.Process(target=self.run_over_range, args=(start_num + i * each_core_work, start_num +
                                                                         (i+1) * each_core_work, OG_HASH, que))
                p.start()  # Letting the thread start running in the background.

            p.join()  # Waiting for the last thread to finish up

            if not que.empty():  # if there is a number in the queue it means that we found the number
                number_found = que.get()
                server_socket.send('True/' + str(number_found))  # Send to server, number found
            else:
                server_socket.send('False/None')  # Send to server number has not been found


if __name__ == '__main__':
    c = Client()  # Creating a new client
    c.start()  # Starting the client
