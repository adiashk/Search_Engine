from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import TweetTokenizer
from document import Document
import re
import utils


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.capital_letters_list = set()
        self.names_list = set()

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # text_tokens = word_tokenize(text)
        # text_tokens = TweetTokenizer().tokenize(text)
        # text += " 123 Thousand"
        # text += " 123 percentage"
        # text += " 10,123"
        # text += " 1010.56"
        # text += " 10.56%"
        # text += " 35 3/4"
        # text += " 1.5618"
        # text += " 10,344.5"
        # text += " Hello"
        # text += " hello"
        text = re.sub('(?<=\D)[.,]|[.,](?=\D)', '', text)
        text_tokens = WhitespaceTokenizer().tokenize(text)
        # text_tokens_without_stopwords = []
        # for term in text_tokens:
        #     if term not in self.stop_words:
        #         if term[0].isupper():
        #             self.capital_letters_list.add(term)  # capital letters
        #             self.names_list.add(term)  # names
        #     text_tokens_without_stopwords.append(term.lower())

        # utils.save_obj(self.capital_letters_list, "capital_letters_list")  # write the capital letters to file
        # utils.save_obj(self.names_list, "names_list")  # write the capital letters to file
        # capital_letters_list_check = utils.load_obj("capital_letters_list")

        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        text_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]

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
        # if tweet_id == "1280966288295317504":
        #     c = "f"
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        # for term in tokenized_text:  # enumerate---------------->
        for index, term in enumerate(tokenized_text):
            # roles:
            self.covert_percent(index, term, tokenized_text)  # replace: Number percent To Number%
            self.convert_numbers(index, term, tokenized_text)

            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document

    def covert_percent(self, index, term, tokenized_text):
        if term.lower() == "percent" or term.lower() == "percentage":
            self.check_number_before_sign_and_replace_word(index, tokenized_text, "%")

    def check_number_before_sign_and_replace_word(self, index, tokenized_text, sign):
        if tokenized_text[index - 1].isdigit():  # number_before_sign
            tokenized_text[index - 1] += sign  # replace_word
            del tokenized_text[index]

    def convert_numbers(self, index, term, tokenized_text):
        if term.lower() == "thousand":
            self.check_number_before_sign_and_replace_word(index, tokenized_text, "K")
        if term.lower() == "million":
            self.check_number_before_sign_and_replace_word(index, tokenized_text, "M")
        if term.lower() == "billion":
            self.check_number_before_sign_and_replace_word(index, tokenized_text, "B")
        if term[0].isdigit():
            term = term.replace(',', '', 1)
            try:
                dec_num = float(term)
                number = int(dec_num)
            except:
                if '/' in term:
                    if tokenized_text[index - 1].isdigit():  # number_before_sign
                        tokenized_text[index - 1] += " " + tokenized_text[index]  # replace_word
                        del tokenized_text[index]
                return
            if dec_num < 1000:
                if number!=dec_num:
                    dot_index = term.index('.')
                    new_num = term[0:dot_index+4]
                    tokenized_text[index] = new_num
            if 1000 <= number < 1000000:
                new_num = round(number / 1000, 3)  # keep 3 digits
                tokenized_text[index] = str(new_num) + "K"
            elif 1000000 <= number < 1000000000:
                new_num = round(number / 1000000, 3)
                tokenized_text[index] = str(new_num) + "M"
            elif 1000000000 <= number:
                new_num = round(number / 1000000000, 3)
                tokenized_text[index] = str(new_num) + "B"
