# Doc to csv of id and full text
import csv

from reader import ReadFile
from configuration import ConfigClass

tweet_ids = []


def read_tweet_ids():
    with open('206345241.csv', mode='r')as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            tweet_ids.append(lines[1])


def write_content_for_tweet_id():
    corpus_path = "C:\\Users\\ASUS\\Desktop\\Data"
    config = ConfigClass(corpus_path)
    r = ReadFile(corpus_path=config.get__corpusPath())
    names = r.get_files_names_in_dir()

    with open("text.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for name in names:
            documents_list = r.read_file_by_name(file_name=str(name))
            for doc in documents_list:
                if doc[0] in tweet_ids:
                    writer.writerow([doc[0], doc[2]])

def find_tweet_id(tweet_id):
    with open('text.csv', mode='r',encoding='utf-8')as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if lines[0] == tweet_id:
                return lines[1]

# read_tweet_ids()
# write_content_for_tweet_id()
print(find_tweet_id('1282081615980769280'))