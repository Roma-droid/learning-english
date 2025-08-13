import random
import time
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import speech_recognition as sr

# Словарь для изучения (русский: английский)
words = {
    "привет": "hello",
    "мир": "world",
    "яблоко": "apple",
    "дом": "house",
    "кот": "cat",
    "собака": "dog",
    "книга": "book",
    "солнце": "sun",
    "вода": "water",
    "огонь": "fire"
}

def record_audio(duration=3, fs=44100):
    """Запись аудио с микрофона"""
    print(f"\nГоворите! Запись идет {duration} секунды...")
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()  # Ожидание окончания записи
        return recording, fs
    except Exception as e:
        print(f"Ошибка записи: {e}")
        return np.zeros((int(fs * duration), 1)), fs

def save_audio(recording, fs, filename='output.wav'):
    """Сохранение аудио в файл"""
    try:
        # Преобразование в 16-битный формат для сохранения
        audio_int16 = (recording * 32767).astype(np.int16)
        write(filename, fs, audio_int16)
        return filename
    except Exception as e:
        print(f"Ошибка сохранения аудио: {e}")
        return None

def recognize_speech(filename='output.wav'):
    """Распознавание речи из аудиофайла"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(filename) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='en-US')
                return text.lower()
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                print("Ошибка сервиса распознавания речи")
                return ""
    except Exception as e:
        print(f"Ошибка распознавания речи: {e}")
        return ""

def play_sound(frequency=440, duration=0.5, volume=0.5, fs=44100):
    """Воспроизведение звука определенной частоты"""
    try:
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        audio = volume * np.sin(2 * np.pi * frequency * t)
        sd.play(audio, samplerate=fs)
        sd.wait()
    except Exception as e:
        print(f"Ошибка воспроизведения звука: {e}")

def play_correct_sound():
    """Звук правильного ответа"""
    play_sound(523.25, 0.3)  # До высокой октавы

def play_incorrect_sound():
    """Звук неправильного ответа"""
    play_sound(261.63, 0.5)  # До (низкий)

def play_game():
    score = 0
    total = len(words)
    mode = ""
    
    print("\n" + "="*50)
    print("Добро пожаловать в продвинутую игру для изучения английских слов!")
    print("="*50)
    
    # Выбор режима игры
    while mode not in ["1", "2"]:
        print("\nВыберите режим игры:")
        print("1 - Текстовый ввод (клавиатура)")
        print("2 - Голосовой ввод (микрофон)")
        mode = input("Ваш выбор (1/2): ").strip()
    
    # Создаем перемешанный список слов для вопросов
    word_list = list(words.items())
    random.shuffle(word_list)
    
    print(f"\nТебе предстоит перевести {total} слов. Поехали!\n")
    
    for russian, english in word_list:
        print(f"↪ Как переводится слово '{russian}'?")
        
        if mode == "1":
            # Текстовый режим
            user_input = input("Ваш перевод: ").strip().lower()
        else:
            # Голосовой режим
            audio, fs = record_audio()
            filename = save_audio(audio, fs)
            user_input = recognize_speech(filename) if filename else ""
            
            if user_input:
                print(f"Распознано: {user_input}")
            else:
                print("❌ Речь не распознана. Попробуйте еще раз.")
                # Повторная попытка
                audio, fs = record_audio(duration=4)
                filename = save_audio(audio, fs)
                user_input = recognize_speech(filename) if filename else ""
                print(f"Распознано: {user_input}" if user_input else "❌ Снова не распознано")
        
        # Проверка ответа
        if user_input == english:
            print("✅ Верно!")
            play_correct_sound()
            score += 1
        else:
            print(f"❌ Неверно. Правильный ответ: '{english}'")
            play_incorrect_sound()
        
        time.sleep(0.5)  # Короткая пауза между вопросами
    
    # Результаты игры
    print("\n" + "="*50)
    print(f"Игра окончена! Твой результат: {score}/{total}")
    print(f"Процент правильных ответов: {score/total:.0%}")
    
    # Звуковой фидбэк по результатам
    if score == total:
        print("🎉 Отлично! Ты знаешь все слова! 👏")
        play_sound(523.25, 1.0)  # До высокой октавы
        play_sound(659.25, 1.0)  # Ми
        play_sound(783.99, 1.0)  # Соль
    elif score >= total * 0.7:
        print("👍 Хороший результат! Продолжай в том же духе!")
        play_sound(523.25, 0.5)  # До высокой октавы
        play_sound(659.25, 0.5)  # Ми
    elif score >= total * 0.4:
        print("💪 Неплохо, но нужно повторить слова.")
        play_sound(392.00, 0.7)  # Соль
    else:
        print("✏️ Тебе стоит уделить больше времени изучению слов.")
        play_sound(261.63, 1.0)  # До (низкий)

if __name__ == "__main__":
    try:
        play_game()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        print("\nХочешь сыграть еще раз? Запусти программу снова!")
