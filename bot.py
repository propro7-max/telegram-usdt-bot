from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_usdt_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=krw"
        data = requests.get(url, timeout=10).json()
        price = data["tether"]["krw"]
        return float(price)
    except Exception:
        return None

def calculate(krw):

    usdt_price = get_usdt_price()

    if usdt_price is None:
        return "PRICE_ERROR"

    if krw <= 400000:
        fee = 30000
    else:
        fee = krw * 0.10

    net = krw - fee

    if net <= 0:
        return None

    usdt = net / usdt_price

    return fee, net, usdt, usdt_price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "원화 금액 입력\n예: 1000000"
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        update.message.text
        .replace(",", "")
        .replace("원", "")
        .strip()
    )

    if not text.isdigit():

        await update.message.reply_text(
            "숫자만 입력해주세요."
        )

        return

    krw = int(text)

    result = calculate(krw)

    if result == "PRICE_ERROR":

        await update.message.reply_text(
            "실시간 시세 조회 실패\n잠시 후 다시 시도해주세요."
        )

        return

    if result is None:

        await update.message.reply_text(
            "금액 부족"
        )

        return

    fee, net, usdt, usdt_price = result

    msg = f"""
입력금액: {krw:,}원

수수료: {fee:,.0f}원
적용금액: {net:,.0f}원

실시간 테더가: {usdt_price:,.1f}원

지급:
{usdt:.2f} USDT
"""

    await update.message.reply_text(msg)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle
    )
)

import asyncio

async def main():
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
