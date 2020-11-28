import json
import operator

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import TweetTokenizer
from document import Document
import re
import utils
import spacy
from collections import Counter
from nltk.stem import PorterStemmer
import json
from emoji import UNICODE_EMOJI


class Parse:

    def __init__(self, stemming):
        self.stop_words = stopwords.words('english')
        self.stemming = stemming
        self.named_entity = None

    def parse_query(self, query):
        tokenized_text = self.parse_sentence(query)
        parse_query = []
        split_url = self.find_url(tokenized_text)  # create set of terms from URL or full text
        split_hashtag = self.find_hashtags(tokenized_text)
        index = 0
        while index < len(tokenized_text):
            term = tokenized_text[index]
            # term = self.remove_signs(term)
            if term == '':
                index += 1
                continue

            # roles :
            term, skip = self.convert_numbers(index, term, tokenized_text)

            if self.stemming:
                term = self.convert_stemming(term)

            parse_query.append(term)
            index += (skip + 1)

        for term in split_url:
            if self.stemming:
                term = self.convert_stemming(term)
            parse_query.append(term)

        for term in split_hashtag:
            if self.stemming:
                term = self.convert_stemming(term)
            parse_query.append(term)

        parse_query.extend(self.named_entity)
        return list(set(parse_query))
        # return [p for p in parse_query if p not in parse_query]

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # text_tokens = word_tokenize(text)
        # text_tokens = TweetTokenizer().tokenize(text)
        # test = 'www.yu.il/it/ RT (RTAF!) ~? 3533 yuval'
        text = re.sub('(?<=\D)[.,!?()~:;"]|[\u0080-\uFFFF]|[.,](?=\D)', '', text)
        # test = re.sub('(?<=\D)[.,)(?:!]|[\u007B-\uFFFF]|[.,!](?=\D)', '', test)
        # test = re.compile(r"[a-zA-Z]+").findall(test)
        # mylist = ['spam', 'ham', 'eggs']
        # t = ' '
        # t = t.join(mylist)
        # print(t)
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        # text_tokens = WhitespaceTokenizer().tokenize(text)
        text_tokens = text.split(" ")

        self.named_entity = self.Named_Entity_Recognition(text_tokens)

        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        text_tokens_without_stopwords = [w for w in text_tokens if w.lower() not in self.stop_words and len(w) > 0]

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
        named_entity = None
        # named_entity = self.Named_Entity_Recognition(full_text)
        tokenized_text = self.parse_sentence(full_text)

        # doc_length = len(tokenized_text)  # after text operations.

        # for term in tokenized_text:  # enumerate---------------->
        tokenized_text_len = len(tokenized_text)
        temp_split_url = []
        #      temp_split_url = self.convert_full_url(url)  # get list of terms from URL
        temp_split_url = self.convert_full_url(url)  # get list of terms from URL
        skip = 0
        temp_split_hashtag = []
        index = 0
        doc_length = 0
        while index < len(tokenized_text):
            term = tokenized_text[index]
            term = self.remove_signs(term)
            if term == '':
                index += 1
                continue

            # index = tokenized_text_len - 1 - i
            # term = self.covert_words(index, term, tokenized_text)  # replace: Number percent To Number%

            # roles :
            term, skip = self.convert_numbers(index, term, tokenized_text)
            temp_split_hashtag, to_delete_Hash = self.convert_hashtag(term, temp_split_hashtag)
            temp_split_url, to_delete_URL = self.convert_url(term, temp_split_url)  # create set of terms from URL or full text
            #   temp_split_url, to_delete_URL = self.convert_url(term, temp_split_url)  # create set of terms from URL or full text

            if self.stemming:
                term = self.convert_stemming(term)
            if not to_delete_Hash:
                if not to_delete_URL:
                    if term not in term_dict.keys():
                        term_dict[term] = 1
                    else:
                        term_dict[term] += 1

            index += (skip + 1)

        for term in temp_split_hashtag:
            if self.stemming:
                term = self.convert_stemming(term)
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        for term in temp_split_url:
            if self.stemming:
                term = self.convert_stemming(term)
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        doc_length = doc_length + len(temp_split_url) + len(temp_split_hashtag)

        amount_of_unique_words = len(term_dict)

        if len(term_dict) > 0:
            most_frequent_term = max(term_dict, key=term_dict.get)
            max_tf = term_dict[most_frequent_term]
        else:
            max_tf = 0

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length,amount_of_unique_words, max_tf, self.named_entity)
        return document

    def remove_signs(self, term):
        if type(term) is str:
            # check if can add to regex
            term = term.replace(':', '')
            # term = term.replace('?', '')
            # term = term.replace('!', '')
            # term = term.replace('(', '')
            # term = term.replace(')', '')
            # new_term=''
            # for c in term:
            #     new_term += c if len(c.encode(encoding='utf_8')) == 1 else ''
            # if re.search(u'[\u0000–\u007f]', term.encode('utf-8')) is True:
            #     term = new_term
            # if '②' in term:
            #     term = term.replace('②', '')
            # for t in term:
            #     if t in UNICODE_EMOJI:
            #         term = term.replace(t, '')
        return term

    def convert_hashtag(self, term, temp_split_hashtag):
        if "#" in term:
            split_hashtag = self.split_hashtag(term)
            temp_split_hashtag.extend(split_hashtag)
            return temp_split_hashtag, True
        return temp_split_hashtag, False

    def split_hashtag(self, tag):
        temp_tag = tag
        pattern = []
        tag = tag.replace('#', '')
        if "_" in tag:  # we_are -> we are
            pattern = tag.split("_")
            new_pattern = []
            for i in pattern:
                new_pattern.extend(re.compile(r"[a-z]+|[A-Z][a-z]+|\d+|[A-Z]+(?![a-z])").findall(i))
            new_term_tag = " "
            new_term_tag = new_term_tag.join(new_pattern)  # #letItBe->let it be
            new_term_tag = new_term_tag.lower()
            new_pattern.append(new_term_tag)
            new_term_tag = new_term_tag.replace(' ', '')
            new_pattern.append("#" + new_term_tag.lower())  # #letItBe-> #letitbe
            pattern = []
            pattern.extend(new_pattern)

        else:
            pattern = re.compile(r"[a-z]+|[A-Z][a-z]+|\d+|[A-Z]+(?![a-z])").findall(tag)
            new_term_tag = " "
            new_term_tag = new_term_tag.join(pattern)  # #letItBe->let it be
            new_term_tag = new_term_tag.lower()
            pattern.append(new_term_tag)
            pattern.append("#" + tag.lower())  # #letItBe-> #letitbe

        pattern = [i for i in pattern if i]
        pattern = [i.lower() for i in pattern if i.lower() not in self.stop_words]
        return pattern

    def find_hashtags(self, text_tokens):
        hashtags = [s for s in text_tokens if "#" in s]
        split_hashtags = []
        # word = []
        for h in hashtags:
            # word = self.split_hashtag(h)
            split_hashtags.extend(self.split_hashtag(h))
        return split_hashtags

    def convert_full_url(self, url):
        if url != "{}":
            tempSplitURL = []
            url = json.loads(url)
            for u in url:
                tempSplitURL.extend(self.split_url(url[u]))
            tempSplitURL = set(tempSplitURL)
            return list(tempSplitURL)
        else:
            return []

    def convert_url(self, term, temp_split_url):
        if "http" in term:
            if len(temp_split_url) > 0:  # there was long URL
                return temp_split_url, True

            urlstokens = self.split_url(term)
            temp_split_url.extend(urlstokens)
            temp_split_url = set(temp_split_url)
            temp_split_url = list(temp_split_url)
            return temp_split_url, True

        return temp_split_url, False

    def split_url(self, tag):

        # pattern = re.compile(r'[\:/?=\-&]+', re.UNICODE)
        # return pattern.findall(self, tag)
        pattern = []
        if tag is None:
            return pattern
        if "www." in tag:
            # tag = tag.replace('www.', '')
            tag = tag.replace('www.', '')
            pattern = re.compile(r'[\//\:/?=\-&+]', re.UNICODE).split(tag)
            pattern += ["www"]
        else:
            pattern = re.compile(r'[\:/?=\-&+]', re.UNICODE).split(tag)
        pattern = [i for i in pattern if i]
        pattern = [i for i in pattern if i.lower() not in self.stop_words]
        return pattern


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


    def convert_numbers(self, index, term, tokenized_text):
        skip = 0
        if term[0].isdigit():
            term = term.replace(',', '')
            if term.isdigit():  # no dots or signs
                term, skip = self.convert_big_numbers(index, term, tokenized_text, skip)

            else:
                try:
                    float(term)  # decimal number
                    term, skip = self.convert_small_numbers(index, term, tokenized_text, skip)
                except:  # sings
                    if not term[len(term) - 1].isdigit():
                        sign = term[len(term) - 1]
                        if term[0:len(term) - 1].isdigit():  # no dots or signs
                            term = term[0:len(term) - 1]
                            new_term, skip = self.convert_big_numbers(index, term, tokenized_text, skip)
                            if new_term == term:
                                term, skip = self.convert_small_numbers(index, term, tokenized_text, skip)
                            else:
                                term = new_term
                            term += sign
            #  unique words
            if index < len(tokenized_text) - 1 - skip:
                after_term = tokenized_text[index + 1 + skip]
                if after_term.lower() == "percent" or after_term.lower() == "percentage":
                    term += '%'
                    skip += 1
                if after_term.lower() == "dollar" or after_term.lower() == "dollars":
                    term += '$'
                    skip += 1
                if after_term.lower() == "thousand":
                    term += 'K'
                    skip += 1
                if after_term.lower() == "million":
                    term += 'M'
                    skip += 1
                if after_term.lower() == "billion":
                    term += 'B'
                    skip += 1

        return term, skip

    def convert_big_numbers(self, index, term, tokenized_text, skip):  # get term that it only digits
        is_changed = False
        number = int(float(term))
        if 1000 <= number < 1000000:
            new_num = round(number / 1000, 3)  # keep 3 digits
            if new_num == int(new_num):
                term = str(int(new_num)) + "K"
            else:
                term = str(new_num) + "K"
            is_changed = True
        elif 1000000 <= number < 1000000000:
            new_num = round(number / 1000000, 3)
            if new_num == int(new_num):
                term = str(int(new_num)) + "M"
            else:
                term = str(new_num) + "M"
            is_changed = True
        elif 1000000000 <= number:
            new_num = round(number / 1000000000, 3)
            if new_num == int(new_num):
                term = str(int(new_num)) + "B"
            else:
                term = str(new_num) + "B"
            is_changed = True

        term, skip = self.convert_divided_numbers(index, term, tokenized_text, skip,
                                                  is_changed)  # 2000 1/3 --> 2K skip in the 1/3
        return term, skip

    def convert_small_numbers(self, index, term, tokenized_text, skip):
        if '.' in term:
            if float(term) > 999:
                term, skip = self.convert_big_numbers(index, term, tokenized_text, skip)
            else:
                dot_index = term.index('.')
                term = term[0:dot_index + 4]
        return term, skip

    def convert_divided_numbers(self, index, term, tokenized_text, skip, is_big):
        if index < len(tokenized_text) - 1:
            after_term = tokenized_text[index + 1]
            if '/' in after_term:
                slash_index = after_term.index('/')
                # if after_term[slash_index-1] is not None and after_term[slash_index + 1] is not None:
                if len(after_term) >= 3:
                    if after_term[slash_index-1].isdigit():
                        if slash_index + 1 < len(after_term) - 1:
                            if after_term[slash_index + 1].isdigit():
                                if not is_big:
                                    term += ' ' + after_term
                            skip += 1
        return term, skip


    def Named_Entity_Recognition(self, text_tokens):
        names = []
        # upper_words = re.compile(r"[A-Z][a-z]+|[A-Z]+(?![a-z])").findall(text)
        # upper_words = [w for w in text_tokens if w[0].isupper() and len(w) > 0]
        upper_words = []
        index = 0
        while index < len(text_tokens):
            term = text_tokens[index]
            if len(term) > 0 and term[0].isupper():
                next_index = index + 1
                while next_index < len(text_tokens):
                    next_term = text_tokens[next_index]
                    if len(next_term) > 0 and next_term[0].isupper():
                        if '-' in next_term:
                            next_term = next_term.replace('-', ' ')
                        term += ' ' + next_term  # add the next word
                        next_index += 1
                    else:
                        break
                index = next_index
                if term.lower() not in self.stop_words:
                    if ' ' in term:
                        names.append(term)
            else:
                index += 1

        counter_names = Counter(names)
        return counter_names


    def convert_stemming(self, term):
        ps = PorterStemmer()
        if term[0].isupper():
            term = ps.stem(term).upper()
        else:
            term = ps.stem(term)
        return term
