import socket
import json
from BlockChain import Blockchain
from multiprocessing import Pool, Queue, Process, Manager
from multiprocessing.pool import ThreadPool
import multiprocessing, socket, logging, os

logging.basicConfig(level=logging.DEBUG)

def threadHandle(connection, address, logger):
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == b"":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            connection.sendall(data)
            logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

def callBack(p):
    logging.debug('callback %r', p)

def processHandle(q):
    logger = logging.getLogger("process-%r" % (os.getpid(),))
    tp = ThreadPool()
    while True:
        (connection, address) = q.get()
        logger.debug("processHandle get connection from Queue")
        tp.apply_async(threadHandle, (connection, address, logger), callback=callBack)

class Node:
    def __init__(self, addr) -> None:
        self.addr = addr
        self.hostname = addr.split(':')[0]
        self.port = int(addr.split(':')[1])
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.peers_addr = []
        with open("./Stable_IP.config") as file:
            self.peers_addr = [line.strip() for line in file]
        if addr in self.peers_addr:
            self.peers_addr.remove(addr)

    def send_addr(self):
        for addr in self.peers_addr:
            hostname = addr.split(':')[0]
            port = int(addr.split(':')[1])
            self.socket.connect((hostname, port))


    def get_addr(self):
        
        pass

    def listening(self, q):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen()
        while True:
            self.logger.debug("Waiting Connection ...")
            conn, address = self.socket.accept()
            self.logger.debug("Got connection and Send it to Queue")
            q.put((conn, address), False)


if __name__ == "__main__":
    node = Node("0.0.0.0:8000")

    try:
        m = Manager()
        q = m.Queue()

        for i in range(multiprocessing.cpu_count()):
            p = Process(target=processHandle, args=(q,))
            p.start()
        logging.info("Node Listening")
        node.listening(q)

    except:
        logging.exception("Unexpected exception")
    
    finally:
        logging.info("Shutting down")

    logging.info("All done")