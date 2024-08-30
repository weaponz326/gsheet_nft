import json
import os
from web3 import Web3
from google_sheets import get_sheet_data
from dotenv import load_dotenv

load_dotenv()

INFURA_URL = os.getenv('INFURA_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

ABI = json.loads('''[
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": false,
                "internalType": "string",
                "name": "player",
                "type": "string"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "score",
                "type": "uint256"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "name": "ScoreRecorded",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "player",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "score",
                "type": "uint256"
            }
        ],
        "name": "recordScore",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getScores",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "string",
                        "name": "player",
                        "type": "string"
                    },
                    {
                        "internalType": "uint256",
                        "name": "score",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct HighScores.Score[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.privateKeyToAccount(PRIVATE_KEY)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def push_data_to_blockchain(data):
    nonce = w3.eth.getTransactionCount(account.address)
    gas_price = w3.eth.gas_price

    for row in data:
        player, score = row[0], int(row[1])
        txn = contract.functions.recordScore(player, score).buildTransaction({
            'chainId': 42161,  # Arbitrum One chain ID
            'gas': 2000000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        signed_txn = account.signTransaction(txn)
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f'Transaction sent: {tx_hash.hex()}')
        nonce += 1

if __name__ == '__main__':
    spreadsheet_id = 'YOUR_SPREADSHEET_ID'
    range_name = 'Sheet1!A1:E10'
    data = get_sheet_data(spreadsheet_id, range_name)
    push_data_to_blockchain(data)
