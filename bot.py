import configparser, logging, sys, os, re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler

from persistence import Persistence

import pyodbc

def userHandler( func ):
    async def inner(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user.username
        if user in context.bot_data['users']:
            return await func(update, context, *args, **kwargs) 

        if user is None:
            replyText = f'No username, create a username first'
        if user not in context.bot_data['users']:
            logging.getLogger().info(f'User {user} tried to use the bot')
            replyText = f'Access denied!'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=replyText)
        return
    return inner

@userHandler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    replyText = f'Welcome {user}!\nJust send a message with the housing serial to get the latest status'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=replyText)

@userHandler
async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    context.bot_data['save'] += msg
    await context.bot.send_message(chat_id=update.effective_chat.id, text=context.context.bot_data['save'])

async def buttonHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    #No update for messages with InlineKeyboard
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    await context.bot.send_message(chat_id=query.message.chat_id, text=query.message.text)

    promise = await context.bot.send_message(chat_id=update.effective_chat.id, text="Getting data...")
    chatID = promise.chat_id
    msgID = promise.message_id
    partID = int(query.data)
    context.bot_data['Testdata'] = "123"

    await query.answer(text=f'Got x stations to look up data')

    replyText = f'{"Station":10}|{"Status":10}\n'
    await context.bot.edit_message_text(replyText, chat_id=chatID, message_id=msgID)


def wrongConfig(section:str, key:str):
    print( f'Error in config file: No key "{key}" in section "{section}"' )
    exit( 1 )

def readConfig(configfile:str):
    config = configparser.RawConfigParser()
    if not len( config.read( configfile ) ):
        print(f"Wrong usage! Couldn't read config file {configfile}")
        print( f'{__file__} [PathToConfigFile]' )
        exit(1)
    
    c = {}
    if 'Database' in config.sections():
        db = {}
        if 'Server' in config['Database']:
            db['server'] = config['Database']['Server']
        else:
            wrongConfig('Database', 'Server')
        if 'Name' in config['Database']:
            db['name'] = config['Database']['Name']
        else:
            wrongConfig('Database', 'Name')
        if 'User' in config['Database']:
            db['user'] = config['Database']['User']
        else:
            wrongConfig('Database', 'User')
        if 'Password' in config['Database']:
            db['pw'] = config['Database']['Password']
        else:
            wrongConfig('Database', 'Password')
        c['db'] = db
    if 'Telegram' in config.sections():
        telegram = {}
        if 'Token' in config['Telegram']:
            telegram['token'] = config['Telegram']['Token']
        else:
            wrongConfig('Telegram', 'Token')

        if 'Users' in config['Telegram']:
            users = [x.strip() for x in config['Telegram']['Users'].split(',')]
        else:
            wrongConfig('Telegram', 'Users')
        telegram['users'] = users

        c['telegram'] = telegram
    return c

def main(debug:bool):
    logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()
    if debug:
        logger.info("Set level to DEBUG")
        logger.setLevel( logging.DEBUG )

    path = os.path.dirname( os.path.realpath(__file__) )
    configfile = ''
    if len(sys.argv) >= 2:
        configfile = os.path.join(path, sys.argv[1])
    else:
        configfile = os.path.join(path, 'config.ini')
    config = readConfig(configfile)

    try:
        cursor = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + config['db']['server'] + ';DATABASE=' + config['db']['name'] + ';UID=' + config['db']['user'] + ';PWD=' + config['db']['pw']).cursor()
    except Exception as e:
        logger.exception("Could not connect to database")
        exit(-2)
    
    cursor = {}   # <-- uncomment to unbreak persistence data
    persistence = Persistence( config['telegram']['users'], cursor )

    application = ApplicationBuilder().token(config['telegram']['token']).persistence(persistence=persistence).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.add_handler( MessageHandler(filters.TEXT & (~filters.COMMAND), save) )

    application.add_handler(CallbackQueryHandler(buttonHandler))
    
    application.run_polling()

if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 2:
        firstArgument:str = sys.argv[2]
        if firstArgument.lower() == 'debug':
            debug = True
    main(debug)