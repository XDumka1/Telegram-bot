import telebot
import os
from config import TOKEN
from rembg import remove
from PIL import Image
import subprocess
import re

bot = telebot.TeleBot(TOKEN)
project_folder = os.path.dirname(os.path.abspath(__file__))
user_choices = {}
waiting_for_count = set()

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if user_id in user_choices:
       del user_choices[user_id] 
    if user_id in waiting_for_count:
        waiting_for_count.discard(user_id)
        
    bot.send_message(message.chat.id, 
    """
Привет! Я бот для обработки изображений!
1. Выбери нужное действие на кнопках ниже
Доступные функции:
• Удалить фон
• Улучшить разрешение
2. После выбора введи число изображений (по умолчанию 1)
3. Отправь изображения
    """)
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_Remove = telebot.types.InlineKeyboardButton(text="Удалить фон", callback_data='RemoveBackground')
    button_Upscale = telebot.types.InlineKeyboardButton(text="Улучшить разрешение", callback_data='Upscale')
    keyboard.add(button_Remove, button_Upscale)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

@bot.message_handler(content_types=['photo', 'document'])
def handle_media(message):
    user_id = message.from_user.id
    choice = user_choices.get(user_id)
    
    if not choice:
        bot.send_message(message.chat.id, "Сначала выберите действие кнопкой!")
        return
    
    user_folder = os.path.join('USERS', str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    choice['processed'] = choice.get('processed', 0) + 1
    processed_count = choice['processed']
    
    if processed_count > choice['count']:
        bot.send_message(message.chat.id, "Все файлы обработаны!")
        if user_id in user_choices:
            del user_choices[user_id]
        return
    
    input_path = os.path.join(user_folder, f"input{processed_count}.png")
    output_path = os.path.join(user_folder, f"output{processed_count}.png")
    
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
    else:
        file_info = bot.get_file(message.document.file_id)
    
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    
    if choice['action'] == "RemoveBackground":
        bot.send_message(message.chat.id, f"Удаляем фон ({processed_count}/{choice['count']})")
        input_img = Image.open(input_path)
        output_img = remove(input_img)
        output_img.save(output_path)
        
    elif choice['action'] == "Upscale":
        bot.send_message(message.chat.id, f"Увеличиваем разрешение ({processed_count}/{choice['count']})")
        command = [
            'realesrgan-ncnn-vulkan.exe', 
            '-i', input_path, 
            '-o', output_path
        ]
        subprocess.run(command, check=True)
        
    with open(output_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
        
    os.remove(input_path)
    os.remove(output_path)
        
    if processed_count == choice['count']:
        bot.send_message(message.chat.id, "Все файлы обработаны!")
        if user_id in user_choices:
            del user_choices[user_id]
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_Remove = telebot.types.InlineKeyboardButton(text="Удалить фон", callback_data='RemoveBackground')
        button_Upscale = telebot.types.InlineKeyboardButton(text="Улучшить разрешение", callback_data='Upscale')
        keyboard.add(button_Remove, button_Upscale)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    
    if user_id in waiting_for_count:
        text = message.text.strip()
        if re.match(r'^\d+$', text):
            count = int(text)
            if user_id in user_choices:
                user_choices[user_id]['count'] = count
                user_choices[user_id]['processed'] = 0
                bot.send_message(message.chat.id, f"Окей! Буду обрабатывать {count} изображений. Отправляй их!")
                waiting_for_count.discard(user_id)
            return
        else:
            bot.send_message(message.chat.id, "Введите только число! Например: 3")
            return
    
    bot.send_message(message.chat.id, "Выберите действие на кнопках!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == 'RemoveBackground':
        user_choices[user_id] = {'action': 'RemoveBackground', 'count': 1, 'processed': 0}
        waiting_for_count.add(user_id)
        bot.edit_message_text("Выбрано: Удалить фон\nВведите количество изображений (по умолчанию 1):\nЛибо отправьте фото", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Ждем количество изображений...")
        
    elif call.data == 'Upscale':
        user_choices[user_id] = {'action': 'Upscale', 'count': 1, 'processed': 0}
        waiting_for_count.add(user_id)
        bot.edit_message_text("Выбрано: Улучшить разрешение\nВведите количество изображений (по умолчанию 1):\nЛибо отправьте фото", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Ждем количество изображений...")

if __name__ == "__main__":
    bot.polling(none_stop=True)
