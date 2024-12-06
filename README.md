# CPEN333_project
Part 1 : Implementing a multithreaded game with graphic user interface :
         We are to implement a simplified snake game in this project.

         
Part 1 -Alternative: Complete implementation of part1 (all in one .py file, include part1_alternative as a part of the name of the file), but with one modification for the implementation related to an important aspect of the game related to this course: e.g. multi-tasking synchronization/communication, GUI, ... . Some examples of acceptable new implementation approaches would be:

* instead of tkinter, using a different GUI framework, such as pygame, ...
* or instead of using the thread-safe queue, using a different thread-safe mechanism for managing and communicating the tasks 
* or ...

Part 2: Simple Chat Application
In this part of the project, you are going to implement a simple chat application. You will use the python 3 standard library modules of socket, multiprocessing, threading and tkiner. No other modules are to be used.

The program consists of three .py files: main.py (use as is), client.py and server.py. The client and server are imported into our main.py, where we will use the main() functions (as see below in the template).

Normally, the server and each of the chat clients run on different machines, but without loss of generally, we are going to implement this application, so that they run on the same computer. You can use the IP address 127.0.0.1 (known as loopback address or localhost) which is a special IP address that refers to the current computer. 
