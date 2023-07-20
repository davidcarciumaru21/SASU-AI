import json
from difflib import get_close_matches
from googletrans import Translator
from gtts import gTTS
import os
import pygame
import speech_recognition as sr

def load_knowledge_base(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_knowledge_base(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question, knowledge_base):
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None

def speak(text, lang='ro'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("bot_response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("bot_response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)  # Adjust the tick rate
    pygame.mixer.music.fadeout(500)  # Stop the music with a fadeout effect
    pygame.mixer.quit()  # Clean up the mixer resources
    os.remove("bot_response.mp3")

def listen_for_response():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Say something...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            user_response = recognizer.recognize_google(audio, language='ro-RO').lower()
            print("User Response:", user_response)
            return user_response
        except sr.UnknownValueError:
            print("Bot: Nu am putut înțelege ceea ce ai spus. Te rog repetă.")
            speak("Nu am putut înțelege ceea ce ai spus. Te rog repetă.", lang='ro')
            return listen_for_response()
        except sr.RequestError:
            print("Bot: Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.")
            speak("Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.", lang='ro')
            return None

def chatbot():
    knowledge_base = load_knowledge_base('knowledge_base.json')

    while True:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Tu: Say something...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source)
                user_input = recognizer.recognize_google(audio, language='ro-RO').lower()
                print("Tu:", user_input)
            except sr.UnknownValueError:
                print("Bot: Nu am putut înțelege ceea ce ai spus. Te rog repetă.")
                speak("Nu am putut înțelege ceea ce ai spus. Te rog repetă.", lang='ro')
                continue
            except sr.RequestError:
                print("Bot: Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.")
                speak("Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.", lang='ro')
                break

            if user_input == 'ieși acum':
                break

            best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                print(f"Bot: {answer}")
                speak(answer, lang='ro')  # Speak the response with Romanian language
            else:
                explanation = "Nu știu răspunsul la întrebarea ta. Te rog explică mai detaliat sau spune 'treci peste' pentru a trece peste."
                print(explanation)
                speak(explanation, lang='ro')  # Speak the explanation
                user_explanation = listen_for_response()
                if user_explanation == 'treci peste':
                    print("Bot: Am înțeles că dorești să trecem peste. Continuăm cu următoarea întrebare.")
                    speak("Am înțeles că dorești să trecem peste. Continuăm cu următoarea întrebare.", lang='ro')
                elif user_explanation:
                    knowledge_base["questions"].append({"question": user_input, "answer": user_explanation})
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    print("Bot: Mulțumesc! Am învățat ceva nou.")
                    speak("Mulțumesc! Am învățat ceva nou.", lang='ro')  # Speak the response with Romanian language

if __name__ == "__main__":
    chatbot()