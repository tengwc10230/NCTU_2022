from concurrent.futures import thread
import queue
import time
import threading
from BlockChain import BlockChain
from multiprocessing import Process, Queue
import logging, os

logging.basicConfig(level=logging.INFO)
q = Queue()
def jobHandler():
    cnt = 0
    while True:
        cmd, result_bc = q.get()
        cnt += 1
        if cnt >= 2:
            break
        # logging.INFO(cmd)
        if cmd == "MINE":
            if result_bc.node_addr == "0.0.0.0:5000":
                logging.INFO(result_bc)
        elif cmd == "UPDATE":
            print(result_bc)



if __name__ == "__main__":
    
    addr1, addr2 = ["0.0.0.0:5000"], ["0.0.0.0:5001"]
    peer1, peer2 = ["0.0.0.0:5001"], ["0.0.0.0:5000"]
    blockchain1 = BlockChain(addr1, peer1)
    blockchain2 = BlockChain(addr2, peer2)
    blockchain1.is_mining = True
    blockchain2.is_mining = True

    # using multiprocess because calculate nonce are CPU bounded
    p1 = Process(target=blockchain1.mining, args=(q,))
    p2 = Process(target=blockchain2.mining, args=(q,))
    
    p1.start()
    p2.start()

    t1 = threading.Thread(target=jobHandler)
    t1.start()
    
    print("Hello")
    
   


    
    