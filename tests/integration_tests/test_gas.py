from web3.exceptions import TimeExhausted

from .utils import ADDRS, CONTRACTS, KEYS, deploy_contract, send_transaction


def test_gas_eth_tx(geth, ethermint):
    tx_value = 10

    # send a transaction with geth
    geth_gas_price = geth.w3.eth.gas_price
    tx = {"to": ADDRS["community"], "value": tx_value, "gasPrice": geth_gas_price}
    geth_receipt = send_transaction(geth.w3, tx, KEYS["validator"])

    # send an equivalent transaction with ethermint
    ethermint_gas_price = ethermint.w3.eth.gas_price
    tx = {"to": ADDRS["community"], "value": tx_value, "gasPrice": ethermint_gas_price}
    ethermint_receipt = send_transaction(ethermint.w3, tx, KEYS["validator"])

    # ensure that the gasUsed is equivalent
    assert geth_receipt.gasUsed == ethermint_receipt.gasUsed


def test_gas_deployment(geth, ethermint):
    # deploy an identical contract on geth and ethermint
    # ensure that the gasUsed is equivalent
    _, geth_contract_receipt = deploy_contract(
        geth.w3,
        CONTRACTS["TestERC20A"])
    _, ethermint_contract_receipt = deploy_contract(
        ethermint.w3,
        CONTRACTS["TestERC20A"])
    assert geth_contract_receipt.gasUsed == ethermint_contract_receipt.gasUsed


def get_gas(w3, contract, i=0):
    if i > 3:
        raise TimeExhausted
    function_input = 10
    gas_price = w3.eth.gas_price
    geth_txhash = (contract.functions
                   .burnGas(function_input)
                   .transact({'from': ADDRS["validator"], "gasPrice": gas_price}))
    try:
        return w3.eth.wait_for_transaction_receipt(geth_txhash, timeout=20)
    except TimeExhausted:
        return get_gas(w3, contract, ++i)


def test_gas_call(geth, ethermint):
    # deploy an identical contract on geth and ethermint
    # ensure that the contract has a function which consumes non-trivial gas
    geth_contract, _ = deploy_contract(
        geth.w3,
        CONTRACTS["BurnGas"])
    ethermint_contract, _ = deploy_contract(
        ethermint.w3,
        CONTRACTS["BurnGas"])

    geth_call_receipt = get_gas(geth.w3, geth_contract)
    ethermint_call_receipt = get_gas(ethermint.w3, ethermint_contract)

    # ensure that the gasUsed is equivalent
    assert geth_call_receipt.gasUsed == ethermint_call_receipt.gasUsed
