import threading
from multiprocessing import Process, Queue

from numpy import block
from requests import request
from BlockChain import BlockChain
from DemoResult import ChainRecord
from flask import Flask, request, jsonify
import logging, os

logging.basicConfig(level=logging.INFO)

q = Queue()
def jobHandler():
    global blockchain
    logger = logging.getLogger("jobHandler")
    while True:
        cmd, result_bc = q.get()
        logger.info(cmd)
        # mining success
        if cmd == "MINE_SUCCESS":
            # Make sure that the currently mined block is on master chain
            if blockchain.master_chain == result_bc[:-1]:
                blockchain = result_bc
            # Re-mining
            else:
                block = result_bc.master_chain[-1]
                t_update = threading.Thread(target=blockchain.update_local_chains, args=(block, q))
                t_update.start()
        # mining fail
        elif cmd == "MINE_FAIL":
            result_bc.is_mining = True
            t_mine_fail = threading.Thread(target=result_bc.mining, args=(q,))
            t_mine_fail.start()
        elif cmd == "UPDATE":
            blockchain = result_bc

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Welcome to LTH Demo!!"

@app.route("/mine", methods=["GET"])
def mine():
    # create child process to mining
    global blockchain, t_mine
    blockchain.is_mining = True
    t_mine = threading.Thread(target=blockchain.mining, args=(q,))
    t_mine.start()

    response = {
        "message": "Start mining new block... ",
        # "new block": blockchain.master_chain[-1]
    }

    return jsonify(response), 200

# get blockchain information
@app.route("/get_info", methods=["GET"])
def get_info():
    global blockchain
    chain_record = ChainRecord()
    chain_record.blockchain = blockchain.master_chain
    response = {
        "node_addr": blockchain.node_addr,
        "master_chain": blockchain.master_chain,
        "backup_chains": blockchain.backup_chains,
        "is_mining": blockchain.is_mining
    }
    return jsonify(response), 200

# get blocks from other node
@app.route("/get_blocks", methods=["POST"])
def get_blocks():
    # get block hash to find missing chain
    request
    pass

# send block to other node
@app.route("/send_block", methods=["POST"])
def send_block():
    global blockchain, t_update
    logger = logging.getLogger("send_block")
    block = request.form.to_dict(flat=True)
    logger.info(block)

    t_update = threading.Thread(target=blockchain.update_local_chains, args=(block, q))
    t_update.start()

    response = {
        "message": "Updating Local Chains...",
        # "new block": blockchain.master_chain[-1]
    }
    return response

if __name__ == "__main__":
    peer_tab = {
        "127.0.0.1:5000": ["127.0.0.1:5001"],
        "127.0.0.1:5001": ["127.0.0.1:5000"],
        "127.0.0.1:5002": ["127.0.0.1:5001"]
    }

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", default="127.0.0.1", type=str, help="host to listen on")
    parser.add_argument("-P", "--port", default=5000, type=int, help="port to listen on")
    args = parser.parse_args()

    host = args.host
    port = args.port
    addr = f'{host}:{port}'
    peer = peer_tab[addr]

    global blockchain
    blockchain = BlockChain(addr, peer)

    job_handle = threading.Thread(target=jobHandler)
    job_handle.start()
    
    app.run(host=host, port=port)

    # job_handle.join()