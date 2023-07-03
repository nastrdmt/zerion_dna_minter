import csv
import random
import time
from eth_utils import to_hex, to_int
from web3 import Web3
from loguru import logger

from config import gwei, delay

class Help:
    def check_status_tx(self, tx_hash):
        logger.info(
            f'{self.address} - жду подтверждения транзакции - https://etherscan.io/tx/{self.w3.to_hex(tx_hash)}...')

        start_time = int(time.time())
        while True:
            current_time = int(time.time())
            if current_time >= start_time + 100:
                logger.info(
                    f'{self.address} - транзакция не подтвердилась за 100 cекунд, начинаю повторную отправку...')
                return 0
            try:
                status = self.w3.eth.get_transaction_receipt(tx_hash)['status']
                if status == 1:
                    return status
                time.sleep(1)
            except Exception as error:
                time.sleep(1)

    def sleep_indicator(self, secs):
        logger.info(f'{self.address} - жду {secs} секунд...')
        time.sleep(secs)

    def check_gas(self):
        try:
            gas = self.w3.eth.gas_price
            gas = self.w3.from_wei(gas, 'gwei')
            logger.info(f'gwei сейчас - {gas}...')
            return gas

        except Exception as e:
            logger.error(e)
            time.sleep(2)
            return self.check_gas()

class Zerion(Help):
    def __init__(self, key):
        self.privatekey = key
        self.w3 = Web3(Web3.HTTPProvider(random.choice(['https://ethereum.publicnode.com', 'https://1rpc.io/eth', 'https://rpc.ankr.com/eth'])))
        self.account = self.w3.eth.account.from_key(self.privatekey)
        self.address = self.account.address
        self.dna_address = Web3.to_checksum_address('0x932261f9Fc8DA46C4a22e31B45c4De60623848bF')

    def mint(self):
        logger.info(f'{self.address} - начинаю минт Zerion Dna...')
        while True:
            # check gas
            gas = self.check_gas()
            if gas < gwei:
                try:
                    tx = {
                        'from': self.address,
                        'to': self.dna_address,
                        "value": 0,
                        'nonce': self.w3.eth.get_transaction_count(self.address),
                        'data': '0x1249c58b',
                        "chainId": self.w3.eth.chain_id,
                        'maxFeePerGas': int(self.w3.eth.gas_price * 1.1),
                        'maxPriorityFeePerGas': int(self.w3.eth.gas_price)
                    }
                    tx['gas'] = self.w3.eth.estimate_gas(tx)
                    sign = self.account.sign_transaction(tx)
                    hash_ = self.w3.eth.send_raw_transaction(sign.rawTransaction)
                    status = self.check_status_tx(hash_)
                    if status == 1:
                        id = to_int(self.w3.eth.get_transaction_receipt(to_hex(hash_)).logs[0].topics[3])
                        logger.success(
                            f'{self.address} - успешно заминтил Zerion Dna {id} - https://etherscan.io/tx/{self.w3.to_hex(hash_)}...')
                        self.sleep_indicator(random.randint(delay[0], delay[1]))
                        return self.address, 'successfully minted'
                    else:
                        logger.info(f'{self.address} - пробую еще раз...')
                        return self.mint()
                except Exception as e:
                        error = str(e)
                        if 'INTERNAL_ERROR: insufficient funds' in error or 'insufficient funds for gas' in error:
                            logger.error(
                                f'{self.address} - не хватает денег на газ, заканчиваю работу через 5 секунд...')
                            time.sleep(5)
                            return self.address, 'no eth'
                        else:
                            logger.error(e)
                            return self.address, 'error'
            else:
                logger.info(f'газ слишком большой - {gwei} gwei, жду понижения...')
                self.sleep_indicator(30)

def write_to_csv(key, address, result):
    with open('result.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['key', 'address', 'result'])
        writer.writerow([key, address, result])
def main():
    with open("keys.txt", "r") as f:
        keys = [row.strip() for row in f]
    print(f'\n{" " * 32}автор - https://t.me/iliocka{" " * 32}\n')
    logger.info(f'Начинаю работу на {len(keys)} кошельков...')
    for key in keys:
        claim = Zerion(key)
        res = claim.mint()
        write_to_csv(key, *res)
    logger.success('Успешный munетинг...')
    print(f'\n{" " * 32}автор - https://t.me/iliocka{" " * 32}\n')
    print(f'\n{" " * 32}donate - EVM 0xFD6594D11b13C6b1756E328cc13aC26742dBa868{" " * 32}\n')
    print(f'\n{" " * 32}donate - trc20 TMmL915TX2CAPkh9SgF31U4Trr32NStRBp{" " * 32}\n')

if __name__ == '__main__':
    main()
