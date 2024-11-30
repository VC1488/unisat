import random
from logger import logger

alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890'

unique_words = set()

while len(unique_words) < 100:
    word_length = random.randint(8, 10)
    word = ''.join(random.choices(alphabet, k=word_length))
    unique_words.add(word)

with open('../data/generated_text.txt', 'w') as file:
    for word in unique_words:
        file.write(word + '\n')

logger.info("Генерация завершена. Слова записаны в 'data/generated_text.txt'.")
