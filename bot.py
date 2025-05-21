import json
import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"
GLOBAL_COOLDOWN = 10
last_executed = 0


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_point(username):
    data = load_data()
    data[username] = data.get(username, 0) + 1
    save_data(data)
    return data[username]


def get_all_points():
    data = load_data()
    if not data:
        return "Ninguém tem rat points ainda."
    return "\n".join(f"{k}: {v} rat points" for k, v in sorted(data.items(), key=lambda i: -i[1]))


async def add_rat_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_executed
    now = time.time()

    if not context.args:
        await update.message.reply_text("Use: /addpoint <username>")
        return

    username = context.args[0]
    points = add_point(username)
    last_executed = now

    if now - last_executed < GLOBAL_COOLDOWN:
        await update.message.reply_text(f"{username} agora tem {points} rat points.")
        return


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_all_points())


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_data({})
    await update.message.reply_text("Todos os rat points foram zerados!")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("addpoint", add_rat_points))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("reset", reset))
    app.run_polling()
