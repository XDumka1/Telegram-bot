import telebot
import os
from config import TOKEN
from rembg import remove
from PIL import Image

bot = telebot.TeleBot(TOKEN)

user_choices = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Привет, я бот для работы с фото")
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_Remove = telebot.types.InlineKeyboardButton(text="Удалить фон", callback_data='RemoveBackground')
    button_Upscale = telebot.types.InlineKeyboardButton(text="Улучшить разрешение",callback_data='Upscale')
    keyboard.add(button_Remove, button_Upscale)
    bot.send_message(user_id, "Выберите действие и отправьте фото", reply_markup=keyboard)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_folder = str(user_id)
    photo_name = 'photo.jpg'
    choice = user_choices.get(user_id)
    
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = os.path.join(user_folder, 'photo.jpg')
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    if choice == "RemoveBackground":
        bot.send_message(message.chat.id, "Удаляем фон!")

        input_path = os.path.join(user_folder, photo_name)
        output_path = os.path.join(user_folder, 'output.png')

        input_img = Image.open(input_path)
        output_img = remove(input_img)
        output_img.save(output_path)

        with open(output_path, 'rb') as file:
            bot.send_document(message.chat.id, file)

        os.remove(input_path)
        os.remove(output_path)
        del user_choices[user_id]

    elif choice == "Upscale":
        bot.send_message(message.chat.id, "Увеличиваем разрешение!")
        del user_choices[user_id]
    else:
        bot.send_message(message.chat.id, "Выберите действие!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'RemoveBackground':
        user_choices[call.from_user.id] = "RemoveBackground"
        bot.answer_callback_query(call.id)
    elif call.data == 'Upscale':
        user_choices[call.from_user.id] = "Upscale"
        bot.answer_callback_query(call.id)

bot.polling()
