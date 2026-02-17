import telebot
import os
from config import TOKEN
from rembg import remove
from PIL import Image
import subprocess

bot = telebot.TeleBot(TOKEN)
project_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = rf'{project_folder}\REAL-ESRGAN'
user_choices = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, 
    """
Привет! Я бот для обработки фото!
1. Выбери нужное действие на кнопках ниже
2. Отправь фото одним сообщением
Доступные функции:
• Удалить фон
• Улучшить разрешение
    """)
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_Remove = telebot.types.InlineKeyboardButton(text="Удалить фон", callback_data='RemoveBackground')
    button_Upscale = telebot.types.InlineKeyboardButton(text="Улучшить разрешение",callback_data='Upscale')
    keyboard.add(button_Remove, button_Upscale)
    bot.send_message(user_id, "Выберите действие и отправьте фото", reply_markup=keyboard)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_folder = f'REAL-ESRGAN/USERS/{str(user_id)}'
    choice = user_choices.get(user_id)
    input_path = os.path.join(user_folder, 'photo.jpg')
    output_path = os.path.join(user_folder, 'output.png')
    
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
        original_dir = os.getcwd()
        os.chdir(project_folder)
        command = [
            'realesrgan-ncnn-vulkan.exe', 
            '-i', rf'USERS\{user_id}\photo.jpg', 
            '-o', rf'USERS\{user_id}\output.png'
        ]
        subprocess.run(command)
        os.chdir(original_dir)

        with open(output_path, 'rb') as file:
            bot.send_document(message.chat.id, file)
        os.remove(input_path)
        os.remove(output_path)
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
