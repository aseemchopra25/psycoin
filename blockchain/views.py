# Default Django Import
from Pychain.settings import STATIC_URL
from django.shortcuts import render

#Custom Imports
import datetime
import hashlib
import json 
import socket
from django.http import JsonResponse, HttpResponse, HttpRequest, response
from uuid import uuid4
from urllib.parse import urlparse
from django.views.decorators.csrf import csrf_exempt 
import requests
# Creating a blockchain class here!

class Blockchain:
    # This is a constructor that initialises a new object created in the blockchain class
    # This basically creates a blockchain when we define it as (somevariable)= Blockchain()
    # This also creates an initial genesis block
    def __init__(self):
        #This consists of the entire block"chain" xD
        self.chain = []
        # We have to define transactions first before creating the block
        self.transactions = []
        # Defaults to nonce=1 and previous_hash = '0' values
        # This is the genesis block with previous hash value of '0'
        self.create_block(nonce = 1, previous_hash = '0')
        #Store all transactions to make them centralised
        #set is user to convert any iterable to sequence of iterable distinct elements
        # sets are unordered, non repeating element iterable modified as passed as argument
        self.nodes = set()


    # Creating the create_block function that we defined in the constructor
    # This block has 4 attributes, index, timestamp, nonce and previous_hash

    def create_block(self,nonce,previous_hash):
        block = {'index':len(self.chain)+1,
                'timestamp':str(datetime.datetime.now()),
                'nonce':nonce,
                'previous_hash':previous_hash,
                'transactions': self.transactions}   
        # Emptying transactions after creating the new block with relevant transactions
        self.transactions = []

        self.chain.append(block)
        return block
    # This returns the last item in the array  
    def get_previous_block(self):
        return self.chain[-1]
    
    # Apart from immutability that it's really tough for a hacker to change the entire blockchain
    # Proof of work is another security measure tht requires a complex problem to solve for a new block to be added
    # It's easy to verify the complex problem's solution but tough to solve it
    # nonces are used to prevent gaming of system
    # it requires huge time and energy which increases as more mners join the network
    # proof of work was originally created as a solution to the growing problem of spam email
    # Mining is competitive but it's more of a lottery than a race
    # Most proof of works get generated within 10 minutes, but to whom it's anybody's guess
    # This proof of work makes it difficult to alter the blockchain as it would require re-mining of all blocks
    
    # This function creates a new nonce
    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False 
        while check_nonce is False:
            hash_operation  = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce +=1
        return new_nonce


    # Creating a hashing function to encode the blocks created

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

        #####WTH!!!!

    # Defining if the chain is valid

    def is_chain_vald(self,chain):
        previous_block = chain[0]
        block_index=1
        while block_index < len(chain):
            block = chain[block_index] 
            if block['previous_hash']!=self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False 
            previous_block = block 
            block_index +=1
        return True
    # Function to add transaction to blockchain object
    def add_transaction(self, sender, receiver, amount, time):
        self.transactions.append({
            'sender':sender,
            'receiver':receiver,
            'amount':amount,
            'time':str(datetime.datetime.now())
        })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    # Function to add a node by specifying the address and network location of the node's address
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) #network location

    def replace_chain(self):
        network = self.nodes # stores all the nodes in the network 
        longest_chain = None 
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_vald(chain):
                    max_length = length
                    longest_chain = chain 
        if longest_chain:
            self.chain = longest_chain
            return True 
        return False
            
# End of class blockchain
# RECAP
# So far we have defined the blockchain class and the internal functions of the blockchain class

# the constructor __init__, 
# create_block, it creates a new block in the block chain with 4 different parameters as defined above 
# get_previous_block finds the last element (block) in the blockchain
# proof_of_work makes it difficult to tamper with the blockchain
# hash returns the sha256 hash of the encoded json block
# is_chain_valid checks the entire blockchain if it's valid or not


# Let's create our blockchain

blockchain = Blockchain()
# Initialisation of a new empty blockchain complete with the intiail constructor

# Creating an address for the node running our server 
# uuids are unique identifiers for 
node_address = str(uuid4()).replace('-','')
root_node = '9208ec265ec34172ab2f823359faaa02' #if you don't change this i will find you!:D

# Mining a new block

def mine_block(request):
    if request.method == 'GET':
        previous_block = blockchain.get_previous_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        block = blockchain.create_block(nonce, previous_hash)
        response = {'message': 'Congratulations, you just mined a block!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'nonce':block['nonce'],
                    'previous_hash':block['previous_hash']}
    return JsonResponse(response, safe = False)


# Now we define a function that gets us the full blockchain

def get_chain(request):
    if request.method == 'GET':
        response = {'chain':blockchain.chain,
                    'length': len(blockchain.chain)}
    return JsonResponse(response, safe = False)


# Check if blockchain is valid using internal function is_chain_valid

def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_vald(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The blockchain is valid'}
        else:
            response = {'message': 'Lmao we got some problem. The blockchain is not valid'}
    return JsonResponse(response, safe = False)

# csrf_exempt lets requests coming from different domains by exempting CSRF token/cookie matching 
# it is not always required, and marks a view as being exempt from the protection ensured by middeware

@csrf_exempt
def connect_node(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No Node", HttpResponse(status=400)
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'All the nodes are now connected. The Psychoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes)}
    return JsonResponse(response)

@csrf_exempt
def add_transaction(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        transaction_keys = ['sender', 'receiver', 'amount', 'time']
        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)
        index = blockchain.add_transaction(received_json['sender'], received_json['receiver'], received_json['amount'], received_json['time'])
        response = {'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)
    
def replace_chain(request):
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one',
            'new_chain': blockchain.chain}
        else:
            response = {'message': 'All good, the chain is the largest one',
            'actual_chain': blockchain.chain}
    return JsonResponse(response)


