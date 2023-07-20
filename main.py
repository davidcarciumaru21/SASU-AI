from difflib import get_close_matches
import speech_recognition as sr
import pygame
from gtts import gTTS
import os

raspunsuri = {
    "bună": "Salut!",
    "ce faci": "Sunt bine, mulțumesc!",
    "cum îți spui": "Mă numesc ChatBot!",
    "pa": "La revedere!",
    # Adăugați mai multe tipare și răspunsuri așa cum aveți nevoie
}

def reda_audio(text, lang='ro'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("bot_response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("bot_response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.fadeout(500)
    pygame.mixer.quit()
    os.remove("bot_response.mp3")

def obtine_raspuns(input_utilizator):
    input_utilizator = input_utilizator.lower()

    # Verificăm dacă inputul este gol
    if not input_utilizator.strip():
        return "Nu ai scris nimic. Te rog să îmi spui ceva."

    # Verificăm dacă inputul se potrivește cu unul dintre tipare
    for tipar, raspuns in raspunsuri.items():
        if tipar in input_utilizator:
            return raspuns

    # Dacă inputul nu se potrivește perfect, căutăm cele mai apropiate cuvinte în tipare
    cuvinte_apropiate = get_close_matches(input_utilizator, raspunsuri.keys(), n=1, cutoff=0.5)
    if cuvinte_apropiate:
        cuvant_apropiat = cuvinte_apropiate[0]
        raspuns_apropiat = raspunsuri[cuvant_apropiat]
        return f'{raspuns_apropiat}'

    return "Îmi pare rău, nu înțeleg. Poți reformula, te rog?"

def listen_for_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Tu: Spune ceva...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            userCommand = recognizer.recognize_google(audio, language='ro-RO').lower()
            print("Tu:", userCommand)
            return userCommand
        except sr.UnknownValueError:
            print("Bot: Nu am putut înțelege comanda ta. Te rog repetă.")
            reda_audio("Nu am putut înțelege comanda ta. Te rog repetă.", lang='ro')
            return listen_for_command()
        except sr.RequestError:
            print("Bot: Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.")
            reda_audio("Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.", lang='ro')
            return None

def main():
    print("ChatBot: Bună! Sunt ChatBot. Spune 'pa' pentru a ieși.")
    while True:
        input_utilizator = listen_for_command()
        if input_utilizator == 'pa':
            print("ChatBot: La revedere!")
            break

        raspuns = obtine_raspuns(input_utilizator)
        print("ChatBot:", raspuns)

        reda_audio(raspuns, lang='ro')  # Redăm răspunsul prin audio

if __name__ == "__main__":
    main()