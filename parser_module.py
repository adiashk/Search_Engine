from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from nltk.tokenize import WhitespaceTokenizer
import re

class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        #text_tokens = word_tokenize(text)
        text = re.sub('(?<=\D)[.,]|[.,](?=\D)', '', text)
        text_tokens = WhitespaceTokenizer().tokenize(text)
        # hashtags
        split_hash = self.find_hashtags(text_tokens)
        # url
        split_url = self.find_url(text_tokens)
        # remove origin urls:
        text_tokens = self.remove_url_from_token(text_tokens)
        # extend
        text_tokens.extend(split_hash)

        text_tokens.extend(split_url)
        # lower&stopwords
        text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document

    def split_hashtag(tag):
        tag = tag.replace('#', '')
        if "_" in tag:
            return tag.split("_")

        pattern = re.compile(r"[a-z]+|[A-Z][a-z]+|\d+|[A-Z]+(?![a-z])")

        return pattern.findall(tag)

    def find_hashtags(self, text_tokens):
        hashtags = [s for s in text_tokens if "#" in s]
        split_hashtags = []
        # word = []
        for h in hashtags:
            # word = self.split_hashtag(h)
            split_hashtags.extend(self.split_hashtag(h))
        return split_hashtags

    def split_url(self, tag):
        # pattern = re.compile(r'[\:/?=\-&]+',re.UNICODE)
        # return pattern.findall(tag)
        return re.compile(r'[\:/?=\-&]+', re.UNICODE).split(tag)

    def find_url(self, text_tokens):
        url = [s for s in text_tokens if "http" in s]
        split_urls = []
        # word = []
        for h in url:
            # word = self.split_hashtag(h)
            split_urls.extend(self.split_url(h))
        return split_urls

    def remove_url_from_token(self, text_tokens):
        text_tokens = [x for x in text_tokens if "http" not in x]
        return text_tokens
