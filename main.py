#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import telebot
from pydub import AudioSegment
from pydub.effects import normalize

# Загружаем переменные окружения из .env файла
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_command_handler(message):
    text = "Just send an audio message and I'll resend you as a voice message with normalized volume"
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['audio'])
def audio_handler(message):
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Создаем временные файлы для обработки
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as input_file:
        input_file.write(downloaded_file)
        input_path = input_file.name
    
    try:
        # Загружаем аудио
        audio = AudioSegment.from_file(input_path)
        
        # Нормализуем громкость
        normalized_audio = normalize(audio)
        
        # Сохраняем нормализованное аудио
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as output_file:
            output_path = output_file.name
        
        normalized_audio.export(output_path, format='ogg', codec='libopus')
        
        # Отправляем голосовое сообщение
        with open(output_path, 'rb') as voice_file:
            bot.send_voice(
                message.chat.id, 
                voice_file, 
                caption=message.caption, 
                caption_entities=message.caption_entities
            )
        
        # Удаляем временные файлы
        os.unlink(output_path)
    
    finally:
        # Всегда удаляем входной файл
        if os.path.exists(input_path):
            os.unlink(input_path)

if __name__ == '__main__':
    bot.infinity_polling()