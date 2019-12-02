import socket
import multiprocessing
import hashlib
import os


#############################################  ANSWER IS: 3735928559 ###################################################


def write_or_create_text_file(data):
    """This function creates a text file on the client's computer"""
    with open('Found number.txt', 'w') as f:
        if data == 'create':  # On the initial run, I need to create a text file if there isn't one
            print 'created text file'
            f.write('False')
        else:
            f.write(data)  # This is used when the number is found, change the value to True


def check_if_found():
    """Since multiprocessing creates an entirely new instance of python, I need a way to share a variable between
     my threads. I chose to make a text file and write in it,
     this function checks if the number has been found already"""
    with open('Found number.txt', 'r') as f:
        data = f.read()
        return data


def check_hash(num):
    """This function gets a number as the input and returns the MD5 hash code of the number that was the input."""
    hashAlgo = hashlib.md5()
    pw = str(num)
    hashAlgo.update(pw.encode('utf-8'))
    hash = hashAlgo.hexdigest()
    return hash


class Client (object):  # The client's class
    def __init__(self):
        """The constructor of the Client class"""
        self.IP = '127.0.0.1'  # The Ip of the client.
        self.PORT = 220  # The port of the client.
        self.cores = 0  # A variable that contains the amount of cores the pc has

    def start(self):
        """Sort of like the main function, it binds a socket connection to the server and gets the jobs that he asks."""
        try:
            print('connecting to IP %s PORT %s' % (self.IP, self.PORT))
            # Create a TCP/IP socket
            global sock
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.IP, self.PORT))

            print('Connected to server!')
            msg = sock.recv(1024)
            print(msg.decode())  # Server's initial message
            self.cores = multiprocessing.cpu_count()  # Now self.cores has the amount of cores that the CPU has
            print "The amount of cores this client has is: " + str(self.cores)
            write_or_create_text_file('create')  # Creates the text file in the client's directory
            self.handle_server_job(sock)

        except socket.error as e:
            print(e)
            sock.close()

    def run_over_range(self, start_num, end_num, hash_needed, que):
        """This function is called on each process and it goes over the range of the numbers that
         the process needs to go over"""
        found = check_if_found()
        while found and start_num != end_num:  # If number not found yet or start num isn't equal to end num
            hash_of_num = check_hash(start_num)
            if hash_of_num == hash_needed:
                print '\r\nnumber found!!!!!!!!!!!\r\n'
                que.put(start_num)  # inserting the value of the number into a queue
                write_or_create_text_file('True')  # Telling all the other processes that we have found the number.
                break
            found = check_if_found()  # Checking maybe another process has found the number
            start_num += 1

    def handle_server_job(self, server_socket):
        found = 'False'  # On initial run it needs to be False (no way someone found it yet).
        while found != 'True':
            job = sock.recv(1024)  # Getting the range and hash from the server
            if 'Unfortunately' in job:  # This is used when we ran out of numbers and the MD5 hash code
                # didn't match any number in the ranged set.
                print job
                os._exit(1)  #Closing the program
            print 'The job is: ' + str(job)
            parts_of_job = job.split('/')  # This splits according to the the protocol the server transfers the details.
            print parts_of_job
            OG_HASH = parts_of_job[0]  # The hash that we will need to compare to.
            start_num = int(parts_of_job[1])
            finish_num = int(parts_of_job[2])
            each_core_work = 1 + ((finish_num-start_num)/self.cores) # How many numbers will each core(process) go over in order to be efficient.
            print start_num, finish_num, each_core_work
            que = multiprocessing.Queue()  # Creating a variable that will allow me to transfer data between processes.
            p = ''
            for i in range(self.cores):  # Running a process on each one of the cores, fully efficient, CPU on 100% use.
                print 'Started process number: ' + str(i+1)  # Adding 1 so it would not start from 0
                print 'These are the args:\r\n' + str(start_num + (i * each_core_work)), \
                        str(start_num + ((i+1) * each_core_work)), OG_HASH, que, '\r\n'
                p = multiprocessing.Process(target=self.run_over_range, args=(start_num + (i * each_core_work), start_num +
                                                                              ((i+1) * each_core_work), OG_HASH, que))
                p.start()  # Letting the thread start running in the background.
            p.join()  # Waiting for the last thread to finish up
            if not que.empty():  # If there is a number in the queue it means that we found the number
                print 'Sending to server found'
                number_found = que.get()  # Getting the final number
                server_socket.send('True/' + str(number_found))  # Send to server, number found
                print server_socket.recv(1024)  # Getting server's final message (A thank you)
            else:
                print 'Sending to server not found'
                server_socket.send('False/None')  # Send to server number has not been found
            found = check_if_found()  # Checking if a process has found the number


if __name__ == '__main__':
    c = Client()  # Creating a new client
    c.start()  # Starting the client
