import json
from difflib import get_close_matches
from googletrans import Translator
from gtts import gTTS
import os
import pygame
import speech_recognition as sr

def loadKknowledgeBase(filePath):
    with open(filePath, 'r') as file:
        return json.load(file)

def saveKnowledgeBase(filePath, data):
    with open(filePath, 'w') as file:
        json.dump(data, file, indent=2)

def findBestMatch(userQuestion, questions):
    matches = get_close_matches(userQuestion, questions, n=1, cutoff=0.7)
    return matches[0] if matches else None

def getAnswerForQuestion(question, knowledgeBase):
    for q in knowledgeBase["questions"]:
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
        pygame.time.Clock().tick(10) 
    pygame.mixer.music.fadeout(500)  
    pygame.mixer.quit() 
    os.remove("bot_response.mp3")

def listen_for_response():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Say something...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            userResponse = recognizer.recognize_google(audio, language='ro-RO').lower()
            print("User Response:", userResponse)
            return userResponse
        except sr.UnknownValueError:
            print("Bot: Nu am putut înțelege ceea ce ai spus. Te rog repetă.")
            speak("Nu am putut înțelege ceea ce ai spus. Te rog repetă.", lang='ro')
            return listen_for_response()
        except sr.RequestError:
            print("Bot: Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.")
            speak("Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.", lang='ro')
            return None

def chatbot():
    knowledgeBase = loadKknowledgeBase('knowledgeBase.json')

    while True:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Tu: Say something...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source)
                userInput = recognizer.recognize_google(audio, language='ro-RO').lower()
                print("Tu:", userInput)
            except sr.UnknownValueError:
                print("Bot: Nu am putut înțelege ceea ce ai spus. Te rog repetă.")
                speak("Nu am putut înțelege ceea ce ai spus. Te rog repetă.", lang='ro')
                continue
            except sr.RequestError:
                print("Bot: Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.")
                speak("Serviciul de recunoaștere vocală nu este disponibil momentan. Te rog încearcă mai târziu.", lang='ro')
                break

            if userInput == 'ieși acum':
                break

            bestMatch = findBestMatch(userInput, [q["question"] for q in knowledgeBase["questions"]])

            if bestMatch:
                answer = getAnswerForQuestion(bestMatch, knowledgeBase)
                print(f"Bot: {answer}")
                speak(answer, lang='ro')
            else:
                explanation = "Nu știu răspunsul la întrebarea ta. Te rog explică mai detaliat sau spune 'treci peste' pentru a trece peste."
                print(explanation)
                speak(explanation, lang='ro')
                userExplanation = listen_for_response()
                if userExplanation == 'treci peste':
                    print("Bot: Am înțeles că dorești să trecem peste. Continuăm cu următoarea întrebare.")
                    speak("Am înțeles că dorești să trecem peste. Continuăm cu următoarea întrebare.", lang='ro')
                elif userExplanation:
                    knowledgeBase["questions"].append({"question": userInput, "answer": userExplanation})
                    saveKnowledgeBase('knowledgeBase.json', knowledgeBase)
                    print("Bot: Mulțumesc! Am învățat ceva nou.")
                    speak("Mulțumesc! Am învățat ceva nou.", lang='ro')


chatbot()