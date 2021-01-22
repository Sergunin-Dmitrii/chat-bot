#!usr/bin/python3
import random
from nltk import edit_distance

BOT_CONFIG = {
        'intents': {
            'hello': {
                'examples':['Привет','Добрый день','Здравствуйте'],
                'responses':['Привет','Здравствуйте','Доброго дня'],
            },
            'bye': {
                'examples': ['Пока','Досвидания','Счастливо'],
                'responses': ['Давай','Пока-пока','Счастливо'],
            },
            #ADD Dictionary
        },
        'failure_phrases': [
            'Не понял. Повтори.',
            'Не знаю, не читал.',
        ]
}

def clear_phrase(text):
    text = text.lower()
    text = ''.join([char for char in text if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьюя -'])
    return text



def classify_intent(replica):
    replica=clear_phrase(replica)
    for intent, intent_data in BOT_CONFIG['intents'].items():
        for example in intent_data['examples']:
            example=clear_phrase(example)
            distance=edit_distance(replica,example)
            if distance / len(example) < 0.3:
                return intent

def get_answer_by_intent(intent):
    if intent in BOT_CONFIG['intents']:
        responses=BOT_CONFIG['intents'][intent]['responses']
        return random.choice(responses)

def generate_answer(replice):
    #TODO
    return #'Привет. Как дела?'

def get_stub():
    failure_phrases=BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

def chat_bot(replica):
    #NLU
    intent=classify_intent(replica)
    
    #Получение ответа

    #Правила выбора ответа
    if intent:
        answer=get_answer_by_intent(intent)
        if answer:
            return answer
    
    #Генеративная модель
    answer=generate_answer(replica)
    if answer:
        return answer 
    
    #заглушка
    answer=get_stub()    
    return answer


if __name__ == '__main__':
    replica=input()
    print(chat_bot(replica))
