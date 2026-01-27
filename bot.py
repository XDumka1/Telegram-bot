import telebot
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет, я бот для улучшения качества фото. Отправьте фото для работы с ним")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_folder = str(user_id)
    
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = os.path.join(user_folder, 'photo.jpg')
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, 'Фотография сохранена.')

bot.polling()
