# MD5-brute-force-implemintation
In this project I created a MD5 brute force in python.\
I have a server side that is using semaphore for multi-threading (creating a thread for each client and client). I also have a client side that is using multi-processing (running a process for each one of the computer's core) to fully use the CPU's capabilities. In addition I used Queue in order to communicate between the processes on the client's side. The more clients that connect to the server and "donate" their CPU power:smiley:, the faster it will take the program to find the requested number.

## To Run: ##
In this project I used python 2.7. As of right now the client's are looking for this number: 3735928559. If you want to run the project on a different number, you will need to change the self.HASH value on the server side which contains the MD5d hash of the number. You will also neded to change `START_NUM` value and the `FINISH_NUM` value according to the range of numbers that you want to check. Currently the start num value is: 3735708558 (very close to the one we hashed so that it would not take too long).\
FYI: The program also creates two text files while running. One will be called `Server found number` (server side), the other one will be called `Found number` (client side). These two text files are used in the program and will contain either True or False. You should not worry about them. I used them to communicate between processes on the client's side, something that was easier and neater then using Queue again.


I hope you enjoy this project, and if you have any suggestions please let me know!

[![MD5 Brute Force implementation (Python)!!](https://i.ibb.co/L5qQnLh/https-i-ytimg-com-vi-b6-Sdx-W8c-OQY-maxresdefault.jpg)](https://www.youtube.com/watch?v=b6SdxW8cOQY "MD5 Brute Force implementation (Python)!!")




