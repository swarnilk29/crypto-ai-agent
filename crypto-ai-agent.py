import openai
from web3 import Web3
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from eth_account import Account
from safe_eth.eth import EthereumClient, EthereumNetwork
from safe_eth.safe.api.transaction_service_api import TransactionServiceApi
from safe_eth.safe import Safe
from hexbytes import HexBytes

from config import (
    TELEGRAM_BOT_TOKEN,
    SAFE_API_URL,
    SAFE_WALLET_ADDRESS,
    ALCHEMY_RPC_URL,
    OPENAI_API_KEY,
    OWNER_PRIVATE_KEY
)

# 🔹 Web3 Connection
w3 = Web3(Web3.HTTPProvider(ALCHEMY_RPC_URL))
ethereum_client = EthereumClient(ALCHEMY_RPC_URL)
safe = Safe(SAFE_WALLET_ADDRESS, ethereum_client)
transaction_service_api = TransactionServiceApi(
    network=EthereumNetwork.MAINNET,
    ethereum_client=ethereum_client
)

def send_safe_tx(amount, recipient):
    amount_wei = int(float(amount) * 10**18)
    safe_tx = safe.build_multisig_tx(
        to=recipient,
        value=amount_wei,
        data=HexBytes(""),
        operation=0,
        safe_nonce=None
    )
    safe_tx.sign(HexBytes(OWNER_PRIVATE_KEY))
    tx_hash = transaction_service_api.post_transaction(safe_tx)
    return tx_hash

# 🔹 Check Balance
async def get_balance(update: Update, context: CallbackContext):
    balance_wei = w3.eth.get_balance(SAFE_WALLET_ADDRESS)
    balance_eth = w3.from_wei(balance_wei, "ether")
    await update.message.reply_text(f"Your wallet balance is {balance_eth:.4f} ETH.")

# 🔹 AI Approval
def ai_decide(amount, recipient):
    openai.api_key = OPENAI_API_KEY

    prompt = f"""
    You are an AI managing a crypto wallet. A user has requested to send {amount} ETH to {recipient}.
    
    - If this is a reasonable request, respond "yes".
    - If this request seems suspicious, respond "no".

    Consider:
    - If the amount is < 1 ETH, it's generally safe.
    - Larger amounts may need verification.

    Respond only "yes" or "no".
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're an AI managing a crypto wallet."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 🔹 Send Crypto Command
async def send_crypto(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /send <amount> <recipient_address>")
        return

    amount = context.args[0]
    recipient = context.args[1]
    decision = ai_decide(amount, recipient)

    if "yes" in decision.lower():
        try:
            tx_hash = send_safe_tx(amount, recipient)
            await update.message.reply_text(f"✅ Transaction Sent! TX Hash: {tx_hash}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("❌ Transaction rejected by AI.")

# 🔹 Start Bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("balance", get_balance))
    application.add_handler(CommandHandler("send", send_crypto))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
