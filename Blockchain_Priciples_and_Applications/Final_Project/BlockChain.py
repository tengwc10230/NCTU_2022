import hashlib
import logging
import threading
import requests
from time import time

from torch import block_diag
from FL_model import Net
import flwr as fl
import os
        
NUM_ZEROS = 4
class BlockChain():
    def __init__(self, node_addr, peer_nodes):
        self.master_chain = []
        self.backup_chains = []
        self.node_addr = node_addr
        self.peer_nodes = peer_nodes
        self.is_mining = False

        # self.nonce_starting_number = 0
        # self.mining_range = 1000000
        self.genesis_block()

    def genesis_block(self):
        block = {
            'index': 0,
            'prev_hash': "",
            'timestamp': 0,
            'nonce': 0,
            'model_hash': "default_model_path",
            'prev_model_acc': 0
        }

        self.master_chain.append(block)

    def infer_model(self, model_hash):
        # in this project we return model accuracy
        acc = 80
        # Net.load_model_by_hash(model_hash)
        # model = TheModelClass(*args, **kwargs)
        # model.load_model(block["model_hash"])
        # model.eval()
        # from DataCenter import get_test1_data, get_test2_acc
        # test1_data = get_test_data(block["nonce"])
        # test2_acc = get_test2_acc(block["nonce"])
        # with torch.no_grad():
        #     for x, label in dataloader:
        #         ...
        return acc

    # verify cur_block is valid
    def verify_block(self, prev_block, cur_block):
        logger = logging.getLogger("BlockChain_verify_block")
        if cur_block["index"] != prev_block["index"]+1:
            logger.error("Index Error")
            return False
        if cur_block["prev_hash"] != self.calculate_hash(prev_block):
            logger.error("Hash Error")
            return False
        if self.calculate_hash(cur_block)[0:NUM_ZEROS] != '0' * NUM_ZEROS:
            logger.error("Hash Error")
            return False
        # if cur_block["model_hash"] == prev_block["model_hash"]:
        #     logger.error("Model Error")
        #     return False
        if cur_block["prev_model_acc"] < prev_block["prev_model_acc"]:
            logger.error("Accuracy Error")
            return False
        # check if previous model accuracy is true
        if self.infer_model(prev_block["model_hash"]) != cur_block["prev_model_acc"]:
            logger.error("Infer Error")
            return False

        return True    
    
    # verify whether the information on BC is reasonable  
    def verify_chain(self, chain):
        '''
            'index' == list index,
            'prev_hash': ,
            'timestamp': time(),
            'nonce': 0,
            'model_hash': "default_model_path",
            'prev_model_acc': 0
        '''
        logger = logging.getLogger("BlockChain_verify_chain")
        # verify all chain
        for idx, block in enumerate(chain):
            if block["index"] != idx:
                logger.error("Index Error")
                return False
            if idx > 0 and block["prev_hash"] != self.calculate_hash(chain[idx-1]):
                logger.error("Hash Error")
                return False 
            if idx > 0 and  self.calculate_hash(block)[0:NUM_ZEROS] != '0' * NUM_ZEROS:
                logger.error("Nonce Error")
                return False
            if idx > 0 and block["prev_model_acc"] < chain[idx-1]["prev_model_acc"]:
                logger.error("Accuracy Error")
                return False

        # verify last two block
        # model inference result must be same as the result record in block
        if len(chain) == 1:
            return True
        elif len(chain) == 2:
            return self.infer_model(chain[-2]["model_hash"]) == chain[-1]["prev_model_acc"]
        else:
            return (self.infer_model(chain[-2]["model_hash"]) == chain[-1]["prev_model_acc"] \
                and self.infer_model(chain[-3]["model_hash"]) == chain[-2]["prev_model_acc"]) 
        
    # add new block to master chain return self
    # mining
    #   verify chain
    #   generate_nonce
    #       calculate_hash
    #   send_block
    def mining(self, q):
        # time.sleep(10)
        logger = logging.getLogger("BlockChain_mining")
        logger.info("Start mining ...")
        while self.is_mining:
            # check if master chain is valid
            if self.verify_chain(self.master_chain):
                block = {
                    'index': self.master_chain[-1]["index"]+1,
                    'prev_hash': self.calculate_hash(self.master_chain[-1]),
                    'timestamp': time(),
                    'nonce': 0,
                    'model_hash': Net.get_model_hash(),
                    'prev_model_acc': self.infer_model(self.master_chain[-1]["model_hash"])
                }
                new_block = self.generate_nonce(block)
                self.is_mining = False
                logger.info("End of mining")

                self.master_chain.append(new_block)
                q.put(["MINE", self])
                
                # # nonce generate fail
                # if new_block == block:
                #     q.put(["MINE_FAIL", self])
                # else:
                #     self.master_chain.append(new_block)
                #     q.put(["MINE_SUCCESS", self])
                #     try:                
                #         self.send_block(block)
                #         logger.info("Send block successed")
                #     except Exception as e:
                #         logger.error(e)
                #         logger.info("Send block failed")
                
            # master chain isn't valid, search longest chain and write to master chain
            else:
                self.backup_chains.insert(0, self.master_chain[:-1])
                self.backup_chains.sort(key=lambda x: len(x), reverse=True)
                self.master_chain = self.backup_chains[0]
                self.backup_chains.pop(0)

    @staticmethod
    def calculate_hash(block):
        header_string = str(block["index"]) + block["prev_hash"] + \
            str(block["timestamp"]) + str(block["nonce"]) + \
            block["model_hash"] + str(block["prev_model_acc"])

        sha = hashlib.sha256()
        sha.update(header_string.encode("utf-8"))
        return sha.hexdigest()

    def generate_nonce(self, block):
        # import time
        # start_num = self.nonce_starting_number
        # block['nonce'] = self.nonce_starting_number

        # if (block['index'] != 0):
        #     while self.nonce_starting_number - start_num < self.mining_range:
        #         if self.calculate_hash(block)[0:NUM_ZEROS] != '0' * NUM_ZEROS:
        #             block['nonce'] += 1
        #             self.nonce_starting_number += 1
        #         else:
        #             # mining success
        #             self.nonce_starting_number = 0
        #             return block
        #         # time.sleep(0.01)
        # block['nonce'] = 0
        if (block['index'] != 0):
            while self.calculate_hash(block)[0:NUM_ZEROS] != '0' * NUM_ZEROS:
                block['nonce'] += 1

        return block
    
    # POST block to peer_nodes_addr/send_block
    def send_block(self, block):
        for node in self.peer_nodes:
            url = f'http://{node}/send_block'
            requests.post(url, data=block)

    # add block to available chain return self
    def update_local_chains(self, block, q):
        logger = logging.getLogger("BlockChain_update")
        logger.info("Get block and update chain...")
        new_chain = []
        for master_block in self.master_chain:
            new_chain.append(master_block)
            # logger.error(self.calculate_hash(master_block))
            if (self.calculate_hash(master_block) == block["prev_hash"]):
                if (self.verify_chain(new_chain)):
                    new_chain.append(block)
                    break
        # add to master chain
        if (new_chain[-1] == block):
            if (len(new_chain) > len(self.master_chain)):
                self.master_chain = new_chain
                logger.info("Master chain changing")
            elif (len(new_chain) > len(self.master_chain)-6):
                self.backup_chains.append(new_chain)
                self.update_backup_chains()
            q.put(["UPDATE", self])
        # search backup chain
        else:
            # for all block in all backup_chains create new chain
            for backup_chain in self.backup_chains:
                new_chain = []
                for backup_block in backup_chain:
                    new_chain.append(backup_block)
                    if (self.calculate_hash(backup_block) == block["prev_hash"]):
                        if (self.verify_chain(new_chain)):
                            new_chain.append(block)
                            break
            
            if (new_chain[-1] == block):
                # backup chain longer than master chain
                logger.info("Backup chain changing")
                if (len(new_chain) > len(self.master_chain)):
                    self.backup_chains.remove(new_chain[:-1])
                    self.backup_chains.insert(0, self.master_chain)
                    self.master_chain = new_chain
                    self.update_backup_chains()

                elif (len(new_chain) > len(self.master_chain)-6):
                    self.backup_chains.remove(new_chain[:-1])
                    self.backup_chains.append(new_chain)
                    self.update_backup_chains()

                q.put(["UPDATE", self])
            else:
                # orphan block
                self.get_loss_chain(block)
                q.put(["GET_BLOCK", self])

    def update_backup_chains(self):
        self.backup_chains.sort(key=lambda x: len(x), reverse=True)
        for backup_chain in self.backup_chains:
            if (len(backup_chain) <= len(self.master_chain)-6):
                self.backup_chains.remove(backup_chain)
    
    def get_loss_chain(self, orphan_block):
        logger = logging.getLogger("BlockChain_get_block")

        payload = {
            "hash": self.calculate_hash(orphan_block)
        }

        for node in self.peer_nodes:
            r = requests.get(f'http://{node}/get_block', params=payload)
            
            if r.status_code == requests.codes.ok:
                orphan_chain = r.json()
                logger.info(orphan_chain)
                if (self.verify_chain(orphan_chain) == False):
                    logger.info("Verify Failed")
                    return
                orphan_idx = orphan_chain.index(orphan_block)
                valid = True
                for idx in range(orphan_idx-1, -1, -1):
                    if orphan_chain[:idx] == self.master_chain:
                        for i in range(idx-1, len(orphan_chain)-1):
                            if (self.verify_block(orphan_chain[i], orphan_chain[i+1]) == False):
                                valid = False
                                break
                        if valid:
                            self.master_chain = orphan_chain
                            logger.info("master_chain equal orphan_chain")
                            return
                    for num, chain in enumerate(self.backup_chains):
                        if orphan_chain[:idx] == chain:
                            for i in range(idx-1, len(orphan_chain)-1):
                                if (self.verify_block(orphan_chain[i], orphan_chain[i+1]) == False):
                                    valid = False
                                    break
                            if valid:
                                self.backup_chains[num] = orphan_chain
                                logger.info("backup_chain equal orphan_chain")
                                return

                logger.info("orphan_chain has been discard")