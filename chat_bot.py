#!usr/bin/python3
import random
from nltk import edit_distance
from big_config import get_bot_config
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


BOT_CONFIG = get_bot_config()
clf = LogisticRegression()
vectorizer = CountVectorizer()

def clear_phrase(text):
    text = text.lower()
    text = ''.join([char for char in text if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьюя -'])
    return text

def load_dataset_for_generator():
    dataset = []
    with open('dialogues.txt') as d_file:
        dialogues_text=d_file.read()
        dialogues=dialogues_text.split('\n\n')

        for dialogue in dialogues:
            replicas=dialogue.split('\n')
            replicas=replicas[:2]

            if len(replicas) == 2:
                question, answer = replicas
                question = clear_phrase(question[2:])
                answer = answer[:2]
                dataset.append([question, answer])
    
    dataset_by_word = {} 
    for question, answer in dataset:
        words = question.split()
        for word in words:
            if word not in dataset_by_word:
                dataset_by_word[word] = []
                dataset_by_word[word].append([question, answer])
    
    dataset_by_word_filtered = {}
    for word, word_dataset in dataset_by_word:
        word_dataset.sort(key = lambda word_data: len(word_data[0]))
        dataset_by_word_filtered[word] = word_dataset[:1000]

    return dataset_by_word_filtered

def try_to_learn_bot():
    texts = []
    intent_names = []
    for intent, intent_data in BOT_CONFIG['intents'].items():
        for example in intent_data['examples']:
            texts.append(example)
            intent_names.append(intent)
    ### Векторизация
    X=vectorizer.fit_transform(texts)
    ### Классификация
    clf.fit(X,intent_names)
    

def classify_intent(replica):
    intent = clf.predict(vectorizer.transform([replica]))[0]
    return intent

def get_answer_by_intent(intent):
    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
        return random.choice(responses)

def generate_answer(replica):
    replica = clear_phrase(replica)
    if not replica:
        return None

    word_dataset_filtered = {}
    word_dataset_filtered = load_dataset_for_generator()
    words = set(replica.split())
    word_dataset = []
    for word in words:
        if word in word_dataset_filtered:
            word_dataset = word_dataset_filtered[word]
            word_dataset +=word_dataset
        
    results = []
    for request, response in word_dataset:
        if abs(len(request) - len(response)) / len(request) < 0.2:
          distance=edit_distance(replica,request)
          if distance / len(request) < 0.2:
              results.append([request, response, distance])

    request, response, distance = random.choice(results, key=lambda three: three[2])    

    return response

def get_stub():
    failure_phrases=BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

def chat_bot(replica):
    #NLU
    
    intent=classify_intent(replica)
   
    if intent != ('bye'):
    #Получение ответа

    #Правила выбора ответа
        if intent:
            answer = get_answer_by_intent(intent)
            if answer:
                return answer
        else:
            #Генеративная модель
            answer = generate_answer(replica)
            if answer:
                return answer
            else:
                #заглушка
                answer = get_stub()    
                return answer
    
    return get_answer_by_intent('bye')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def run_bot(update: Update, context: CallbackContext) -> None:
   
    response = chat_bot(update.message.text)
    update.message.reply_text(response)

def main():
    """Start the bot."""
    updater = Updater("1540808164:AAFmJ6OsncLaXiOxWipLzVjWS2Fuq26jXZc", use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_bot))
    
    try_to_learn_bot()

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()