from datetime import datetime
import telebot
import os
from telebot import types

os.environ['CURL_CA_BUNDLE'] = ""
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)


def get_control_buttons(show_return=False):
    markup = types.InlineKeyboardMarkup()
    buttons = []
    if show_return:
        buttons.append(types.InlineKeyboardButton(text='Go back ⬅️', callback_data='agree'))
    buttons.append(types.InlineKeyboardButton(text='Help 🆘', callback_data='help_info'))
    markup.add(*buttons)
    return markup


def send_help_message(chat_id, message_id, is_verified=False):
    markup = types.InlineKeyboardMarkup()
    btn_admin1 = types.InlineKeyboardButton(text='Support 🔧', url='YOUR_URL')
    btn_admin2 = types.InlineKeyboardButton(text='Second support 🔧', url='YOUR_URL')
    back_callback = 'back_to_verified' if is_verified else 'agree'
    btn_back = types.InlineKeyboardButton(text='Go back ⬅️', callback_data=back_callback)
    markup.row(btn_admin1, btn_admin2)
    markup.row(btn_back)

    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text="🆘 Support Service\n\n"
                                   "If you have any questions, write to the administrators:",
                              reply_markup=markup, parse_mode='Markdown')
    except:
        bot.send_message(chat_id, "🆘 Support Service\n\n"
                                  "If you have any questions, write to the administrators:",
                         reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Read the rules 📖', callback_data='rule_1'))
    bot.send_message(message.chat.id,
                     f"Hi, {message.from_user.first_name}! 👋\n\n"
                     "Please read the 4 rules to access the bot.",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

    if call.data == 'rule_1':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='I accept the rules ➡️', callback_data='rule_2'))
        bot.send_message(call.message.chat.id,
                         "🔴 By continuing to use the bot, you confirm that you are of legal age (18+).",
                         reply_markup=markup)

    elif call.data == 'rule_2':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='I accept the rules ➡️', callback_data='rule_3'))
        bot.send_message(call.message.chat.id, "🔴 You assume full responsibility for viewing the content.",
                         reply_markup=markup)

    elif call.data == 'rule_3':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='I accept the rules ➡️', callback_data='rule_4'))
        bot.send_message(call.message.chat.id, "🔴 The administration assumes no responsibility for your actions.",
                         reply_markup=markup)

    elif call.data == 'rule_4':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='I agree ✅', callback_data='agree'),
                   types.InlineKeyboardButton(text='I disagree ❌', callback_data='disagree'))
        bot.send_message(call.message.chat.id,
                         "🔴 You acknowledge that access is voluntary.\n\n"
                         "Confirm your consent:",
                         reply_markup=markup)

    elif call.data == 'agree':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Enter your age 📅\n\n"
                                                     "▫️ In the format: DD.MM.YYYY",
                               reply_markup=get_control_buttons())
        bot.register_next_step_handler(msg, check_age)

    elif call.data == 'disagree':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Go back ⬅️', callback_data='rule_1'))
        bot.send_message(call.message.chat.id, "⛔️ Access restricted ⛔️\n\n"
                                               "You must agree to the rules.",
                         reply_markup=markup)

    elif call.data == 'help_info':
        is_verified = "Verification successful" in (call.message.text or "")
        send_help_message(call.message.chat.id, call.message.message_id, is_verified)

    elif call.data == 'back_to_verified':
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(text='Channel 1 🔗', url='YOUR_URL'),
                   types.InlineKeyboardButton(text='Channel 2 🔗', url='YOUR_URL'))
        markup.row(types.InlineKeyboardButton(text='Help 🆘', callback_data='help_info'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Verification successful ✅\n\n"
                                   "The channel's content is now available to you! 🔥",
                              reply_markup=markup)


def check_age(message):
    if not message.text or message.text.startswith('/'): return
    try:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

        try:
            bot.delete_message(message.chat.id, message.message_id - 1)
        except:
            pass

        birth_date = datetime.strptime(message.text, "%d.%m.%Y")
        today = datetime.today()

        if birth_date > today:
            msg = bot.send_message(message.chat.id,
                                   "❗️ You are deceiving me ❗️\n\n"
                                   "▫️ Please enter your real date of birth.\n\n"
                                   "Click 'Go Back ⬅️'\n"
                                   "To continue",
                                   reply_markup=get_control_buttons(show_return=True),
                                   parse_mode='Markdown')
            bot.register_next_step_handler(msg, check_age)
            return

        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age >= 18:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(text='Channel 1 🔗', url='YOUR_URL'),
                       types.InlineKeyboardButton(text='Channel 2 🔗', url='YOUR_URL'))
            markup.row(types.InlineKeyboardButton(text='Help 🆘', callback_data='help_info'))
            bot.send_message(message.chat.id, "Verification successful ✅\n\n"
                                              "The channel's content is now available to you! 🔥",
                             reply_markup=markup)

        else:
            bot.send_message(message.chat.id,
                             f"⛔️ Access restricted ⛔️\n\n"
                             f"Strictly 18+ entry!\n\n"
                             f"But you are only {age} years old 👶\n\n"
                             f"Made a mistake with the date? Click the button below",
                             reply_markup=get_control_buttons(show_return=True),
                             parse_mode='Markdown')
            return

    except:
        try:
            bot.delete_message(message.chat.id, message.message_id - 1)
        except:
            pass
        msg = bot.send_message(message.chat.id, "You made a mistake 🔄\n\n"
                                                "Enter the date: DD.MM.YYYY",
                               reply_markup=get_control_buttons())
        bot.register_next_step_handler(msg, check_age)


print("The bot is enabled...")
bot.infinity_polling()