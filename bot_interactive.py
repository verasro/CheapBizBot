import os, asyncio, logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from flight_core import run_once

load_dotenv()
logging.basicConfig(level=logging.INFO)

PREFS = {
    "origin": "GIG",
    "dest": "MIA",
    "start_date": "2025-05-22",
    "end_date": "2025-06-30",
    "max_price": 2500,
    "max_stops": 1,
    "max_layover": 2.0
}

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bot iniciado! Use /status para ver filtros."
    )
    ctx.job_queue.run_repeating(job_search, 6*60*60, first=0,
                                chat_id=update.effective_chat.id)

async def cmd_status(update: Update, ctx):
    p = PREFS
    await update.message.reply_text(
        f"Rota: {p['origin']}→{p['dest']}\n"
        f"Datas: {p['start_date']} → {p['end_date']}\n"
        f"Limite: US$ {p['max_price']} | Escalas ≤ {p['max_stops']} | "
        f"Lay-over ≤ {p['max_layover']} h"
    )

async def cmd_rota(update: Update, ctx):
    try:
        PREFS["origin"], PREFS["dest"] = ctx.args[0].upper(), ctx.args[1].upper()
        await update.message.reply_text("✔️ Rota atualizada.")
    except:
        await update.message.reply_text("Uso: /rota GIG MIA")

async def cmd_datas(update: Update, ctx):
    try:
        PREFS["start_date"], PREFS["end_date"] = ctx.args[0], ctx.args[1]
        await update.message.reply_text("✔️ Datas atualizadas.")
    except:
        await update.message.reply_text("Uso: /datas 2025-05-22 2025-06-30")

async def cmd_limite(update: Update, ctx):
    try:
        PREFS["max_price"] = float(ctx.args[0])
        await update.message.reply_text("✔️ Limite atualizado.")
    except:
        await update.message.reply_text("Uso: /limite 3000")

async def job_search(ctx: ContextTypes.DEFAULT_TYPE):
    best = run_once(**PREFS)
    if best:
        msg = (f"🔥 Exec {PREFS['origin']}→{PREFS['dest']} {best['date']}  "
               f"{best['stops']} escala(s) • {best['layover']}h • "
               f"US$ {best['price']:.0f}")
        await ctx.bot.send_message(ctx.job.chat_id, msg)

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Falta TELEGRAM_BOT_TOKEN no .env")
        return
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("rota", cmd_rota))
    app.add_handler(CommandHandler("datas", cmd_datas))
    app.add_handler(CommandHandler("limite", cmd_limite))

    await app.run_polling()


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN no .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("rota", cmd_rota))
    app.add_handler(CommandHandler("datas", cmd_datas))
    app.add_handler(CommandHandler("limite", cmd_limite))

    app.run_polling()   # inicia e mantém o bot ativo
