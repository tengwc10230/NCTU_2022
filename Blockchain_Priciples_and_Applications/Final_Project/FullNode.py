import threading
from multiprocessing import Process, Queue
from queue import Queue
from requests import request
from BlockChain import BlockChain
from DemoResult import ChainRecord
from flask import Flask, request, jsonify
import logging
import copy

logging.basicConfig(level=logging.INFO)

q = Queue()
def jobHandler():
    global blockchain
    logger = logging.getLogger("jobHandler")
    while True:
        cmd, result_bc = q.get()
        logger.info(cmd)
        logger.info(result_bc.master_chain)
        # mining success
        if cmd == "MINE":
            if blockchain.master_chain == result_bc.master_chain[:-1]:
                blockchain = result_bc
                try:                
                    blockchain.send_block(blockchain.master_chain[-1])
                    logger.info("Send block successed")
                except Exception as e:
                    logger.error(e)
                    logger.info("Send block failed")
            else:
                # re-mining
                logger.info("Re-mining...")
                new_bc = copy.deepcopy(blockchain)
                new_bc.is_mining = True
                t_remine = threading.Thread(target=new_bc.mining, args=(q,))
                t_remine.start()
        if cmd == "GET_BLOCK":
            blockchain = result_bc

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Welcome to LTH Demo!!"

@app.route("/mine", methods=["GET"])
def mine():
    # create child process to mining
    global blockchain
    bc_copy = copy.deepcopy(blockchain)
    bc_copy.is_mining = True
    t_mine = threading.Thread(target=bc_copy.mining, args=(q,))
    t_mine.start()

    return "Start mining new block... ", 200

# get blockchain information
@app.route("/get_info", methods=["GET"])
def get_info():
    global blockchain
    # chain_record = ChainRecord()
    # all_node_chain = []
    # for idx, block in enumerate(blockchain.master_chain):
    #     all_node_chain.append(block)
    #     for backup_chain in blockchain.backup_chains:
    #         if backup_chain[idx] != block:
    #             all_node_chain.append(backup_chain[idx])

    # chain_record.blockchains = all_node_chain
    # chain_record.re_calcu_all_block()
    # chain_record.show_chain()

    response = f"node_addr: {blockchain.node_addr}<br/>\
                 master_chain: {blockchain.master_chain}<br/>\
                 backup_chains: {blockchain.backup_chains}"
                
    
    return response, 200

# get blocks from other node
@app.route("/get_block", methods=["GET"])
def get_block():
    global blockchain
    block_hash = request.args.get('hash')
    # send longest chain with hash block back to client
    for idx in range(len(blockchain.master_chain)-1, -1, -1):
        if blockchain.calculate_hash(blockchain.master_chain[idx]) == block_hash:
            return jsonify(blockchain.master_chain)
    for backup_chain in blockchain.backup_chains:
        for idx in range(len(backup_chain)-1, -1, -1):
            if blockchain.calculate_hash(blockchain.master_chain[idx]) == block_hash:
                return jsonify(backup_chain)
    
    # if no hash block just return master chain
    return jsonify(blockchain.master_chain)

# send block to other node
@app.route("/send_block", methods=["POST"])
def send_block():
    global blockchain
    logger = logging.getLogger("send_block")
    block = request.form.to_dict(flat=True)
    block["index"] = int(block["index"])
    block["timestamp"] = float(block["timestamp"])
    block["nonce"] = int(block["nonce"])
    block["prev_model_acc"] = int(block["prev_model_acc"])

    logger.info(block)
    t_update = threading.Thread(target=blockchain.update_local_chains, args=(block, q))
    t_update.start()

    return "Updating Local Chains..."

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