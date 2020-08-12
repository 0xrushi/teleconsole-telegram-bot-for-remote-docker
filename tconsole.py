from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import signal
import sys
import subprocess
import multiprocessing
import time
import io
#python-telegram-bot=12.8               

def run(update, context):
    data = None
    process = subprocess.Popen(
        "teleconsole", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Process started with PID:", process.pid)
    for i in range(5):
        data = process.stdout.readline()
    print(data.decode())
    context.user_data['process'] = process
    update.message.reply_text(data.decode(
        'ascii').rstrip().replace("[1m", "").replace("[0m", ""))


def errorPrint(data):
    sys.stderr.write(data)
    sys.stderr.write("\n")
    sys.stderr.flush()


if(float(sys.version.split(" ")[0].split(".")[0]) < 3):
    errorPrint("Wrong python version, sorry try with python3!")
    sys.exit(-1)
if(not os.path.exists("/bin/sh")):
    errorPrint("Sorry, subprocess wont work without sh, please install coreutils or something similar for your distribition!")
    sys.exit(-1)
data = os.popen("/bin/which teleconsole").read()
if("bin/teleconsole" not in data):
    errorPrint("Please install teleconsole, then try again!")
    sys.exit(-1)


# bot-------------------------------------------------------------------------------------------------------
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')
    context.user_data['process'] = None


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def generate_session(update, context):
    process = multiprocessing.Process(target=run(update, context))
    process.start()


def close_session(update, context):
    p = context.user_data['process']
    p.kill()
    # Send the signal to all the process groups
    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text="Process Killed"
    )


def main():
    updater = Updater(
        "TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("close", close_session))
    dp.add_handler(CommandHandler("generate_token", generate_session))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
