import sqlite3
from string_func import *

#This is the class to handle the words in the documents, this saves the words in the database when a new document is read and also maintains a dictionary at runtime for a O(1) search complexity as python dictionary provides
# a O(1) complexity for searching.
class Word:
    #Format word : [[doc_id,[indexes],[doc_id,[indexes]]
    words = {}
    def __init__(self,word,doc_id,indexes):
        #This function will only be used when reading data from the database

        #This will split the indexes and return a list of indexes with a comma ","
        indexes = list(map(int,indexes.split(",")))
        self.word   = word
        self.doc_id = doc_id
        self.indexes= indexes

        if self.word in Word.words:
            #This will check if the word already exist in the dictionary then simply append the index of the word in the list of indexes with the doc_id
            Word.words[self.word].append([self.doc_id,self.indexes])
        else:
            #This will check if the word does not exist then make a new entry in the dictionary and then append in the list the doc_id and indexes
            Word.words[self.word] = []
            Word.words[self.word].append([self.doc_id, self.indexes])

    @classmethod
    def create_object(cls,word,doc_id,indexes):
        #This function will only be used when a new doc is being added from the program
        conn = sqlite3.connect('inverted.db')
        c = conn.cursor()
        indexes_for = ",".join(list(map(str,indexes)))
        c.execute("INSERT INTO word VALUES(?,?,?)",(word,doc_id,indexes_for))
        conn.commit()
        conn.close()
        return cls(word,doc_id,indexes_for)

    @classmethod
    def create_indexes(cls,doc_id,doc_name,doc):
        #This function is a custom split function which will:
        # 1) split a string with spaces
        # 2) normalize the word i.e remove the commas and hyphens to create an entry in the dictionary
        # 3) check for multiwords in a single word extracted and calculate the indexes to be save for example Rabin-Karp into 3 words [Rabin-Karp,Rabin,Karp]
        # 4) save the word in the dictionary with the indexes or append the indexes for duplicate words

        words = []
        word_dict = {}
        length_doc = len(doc)
        pointer = 0
        previous= 0
        while pointer<length_doc:
            if doc[pointer]==' ' or doc[pointer]=='\n' or (pointer==(length_doc-1)):
                if doc[previous:pointer+1] != ' ':
                    if pointer==(length_doc-1):
                        #FIRST NORMALIZE WORD THEN APPEND
                        words_list = Word.normalize_word(doc[previous:pointer+1])

                        if words_list[0]!= '-' and words_list[0]!= '' and words_list[0]!= ' ':
                            check = words_list[0]
                            for each in range(len(words_list)):

                                indexx = StringOp.RabinKarp(check, words_list[each], 256, 101)
                                words_list[each] = [previous + indexx[0], words_list[each]]
                            for each in words_list:
                                words.append(each)
                                if each[1] in word_dict:
                                    word_dict[each[1]].append(each[0])
                                else:
                                    word_dict[each[1]] = [each[0]]
                    else:
                        # FIRST NORMALIZE WORD THEN APPEND
                        words_list = Word.normalize_word(doc[previous:pointer])
                        if words_list[0] != '-' and words_list[0] != '' and words_list[0]!= ' ':

                            check = words_list[0]
                            for each in range(len(words_list)):
                                indexx = StringOp.RabinKarp(check, words_list[each], 256, 101)
                                words_list[each] = [previous + indexx[0], words_list[each]]
                            for each in words_list:
                                words.append(each)
                                if each[1] in word_dict:
                                    word_dict[each[1]].append(each[0])
                                else:
                                    word_dict[each[1]] = [each[0]]
                previous = pointer+1
                if previous >= length_doc:
                    break
                else:
                    while (previous<length_doc) and (doc[previous]=='\n' or doc[previous] == ' '):
                        previous+=1

                pointer=previous
            else:
                pointer+=1
        # print(word_dict)
        #This will create a Word object for each word searched in the document
        for k,v in word_dict.items():
            Word.create_object(k,doc_id,v)

    @classmethod
    def normalize_word(cls,word):
        #This function will normalize the word to be saved in the dictionary so that 'abc' becomes abc when saved. This returns a list of all possible keys like rabin-karp => ['rabin-karp'.'rabin','karp'].
        word=list(word)
        wordd_dic = {"'s":0,"‘s":0,"’s":0}
        for x in range(len(word)-1):
            if word[x]+word[x+1] in wordd_dic:
                word.pop(x+1)
                word.pop(x)

        word_dict={'"':0,"'":0,"!":0,"`":0,".":0,"(":0,")":0,"{":0,"}":0,"/":0,"\\":0,":":0,"'s":0,"[":0,"]":0,"<":0,">":0,",":0,"‘":0,"’":0,"?":0}
        new_word_list = []
        new_word = ''
        for each in range(len(word)):
            if word[each] in word_dict:
                pass
            else:
                new_word +=word[each]
        new_word_list.append(new_word.lower())
        for each in range(len(new_word)):
            if new_word[each] == '-':
                new_word_list.append("".join(new_word[:each]).lower())
                new_word_list.append("".join(new_word[each+1:]).lower())

        return new_word_list

class Document:
    document = {}
    code = 'D000'
    def __init__(self,doc_id,doc_name,doc):
        Document.code = doc_id
        self.doc_id  = doc_id
        self.doc_name= doc_name
        self.doc     = doc
        Document.document[self.doc_id] = self

    @classmethod
    def create_object(cls,doc_name,doc):
        #This Function will be used to add a document to the database
        #While adding the document it will also update the word table with indexes
        def gen_code():
            x = Document.code
            y = x[1:]
            y = int(y) + 1
            y = str(y)
            while len(str(y)) != 3:
                y = '0' + y
            y = x[0] + y
            return y
        doc_id = gen_code()
        conn = sqlite3.connect("inverted.db")
        c = conn.cursor()
        c.execute("INSERT INTO document VALUES(?,?,?)",(doc_id,doc_name,doc))
        conn.commit()
        conn.close()

        #Here indexes are created and saved
        Word.create_indexes(doc_id,doc_name,doc)
        return cls(doc_id,doc_name,doc)

class Main:
    @classmethod
    def fetch_all(cls):
        conn = sqlite3.connect('inverted.db')
        d = conn.cursor()
        w = conn.cursor()

        d.execute("SELECT * FROM document")
        w.execute("SELECT * FROM word")

        for all in d.fetchall():
            Document(all[0],all[1],all[2])
        for all in w.fetchall():
            Word(all[0],all[1],str(all[2]))

class Search:
    # This is the main search class
    @classmethod
    def search_single_word(cls,user_query):
        # Main.fetch_all()
        user_query = user_query.strip()

        #Creates a list of all normalized possibilities of the user query
        list_words = Search.normalize_word(user_query)
        searched_indexes = {}
        for each in list_words:
            try:
                searched_indexes[each] = Word.words[each]
            except:
                pass
        #This will return a dictionary in the format {'word':[[doc_id1,[index1, index2...]],[doc_id2,[index1, index2...]]]
        return searched_indexes

    @classmethod
    def multi_word_query(cls,user_query):
        #First Split the words in the query
        #Normalize each word for a search in our dictionary
        #create a list for each word {'doc_id','doc_id'}

        #This will return the search query with first priority for the AND operator for splitted words and then the OR operator for the searched words.

        #This will return a dictionary in the format {'doc_id':{'word':[index1,index2....],'word2':[index1,index2.....]}}

        list_words = Search.create_tokens(user_query)
        searched_indexes = {}
        for each in list_words:
            try:
                searched_indexes[each] = Word.words[each]
            except:
                pass
        for k,v in searched_indexes.items():
            searched_indexes[k] = dict(tuple(v))
        list_of_sets_doc_ids = []
        for k,v in searched_indexes.items():
            list_of_sets_doc_ids.append(set(v.keys()))
        intersection = set.intersection(*list_of_sets_doc_ids)
        # print(searched_indexes)
        if intersection!=set():
            final_dict = {}
            for each in intersection:
                for k, v in searched_indexes.items():
                    if each in v:
                        try:
                            final_dict[each][k] = searched_indexes[k][each]
                        except:
                            final_dict[each] = {k: searched_indexes[k][each]}
            return final_dict
        else:
            sum_intersection = {}
            for each in list_of_sets_doc_ids:
                for abc in each:
                    try:
                        sum_intersection[abc]+=1
                    except:
                        sum_intersection[abc]=1
            max_sum = max(sum_intersection.values())
            new_set = set()
            for k,v in sum_intersection.items():
                if v==max_sum:
                    new_set.add(k)
            final_dict = {}
            for each in new_set:
                for k,v in searched_indexes.items():
                    if each in v:
                        try:
                            final_dict[each][k] = searched_indexes[k][each]
                        except:
                            final_dict[each] = {k:searched_indexes[k][each]}


            return final_dict


    @classmethod
    def create_tokens(cls,doc):
        words = []
        length_doc = len(doc)
        pointer = 0
        previous = 0

        while pointer < length_doc:
            if doc[pointer] == ' ' or doc[pointer] == '\n' or (pointer == (length_doc - 1)):
                if doc[previous:pointer+1] != ' ':
                    if pointer == (length_doc - 1):
                        # FIRST NORMALIZE WORD THEN APPEND
                        words_list = Search.normalize_word(doc[previous:pointer+1].strip())
                        if words_list[0] != '-' or words_list[0] != '':
                            for each in words_list:
                                words.append(each)
                    else:
                        # FIRST NORMALIZE WORD THEN APPEND
                        words_list = Search.normalize_word(doc[previous:pointer])
                        if words_list[0] != '-' or words_list[0] != '':
                            for each in words_list:
                                words.append(each)

                previous = pointer + 1
                if previous >= length_doc:
                    break
                else:
                    while (previous < length_doc) and (doc[previous] == '\n' or doc[previous] == ' '):
                        previous += 1

                pointer = previous
            else:
                pointer += 1
        return words

    @classmethod
    def CountWords(cls,text):
        words = []
        pointer = 0
        for x in range(len(text)):
            if x == len(text)-1:
                if text[pointer:x+1].strip() == '':
                    pass
                else:
                    words.append(text[pointer:x+1])
            elif text[x] == ' ':
                if text[pointer:x].strip() == '':
                    pass
                else:
                    words.append(text[pointer:x])
                    pointer=x
        return len(words)


    @classmethod
    def normalize_word(cls,word):
        # This function will normalize the word to be saved in the dictionary so that 'abc' becomes abc when saved. This returns a list of all possible keys like rabin-karp => ['rabin-karp'.'rabin','karp'].
        original_word = word
        word = list(word)
        wordd_dic = {"'s": 0, "‘s": 0, "’s": 0}
        for x in range(len(word) - 1):
            if word[x] + word[x + 1] in wordd_dic:
                word.pop(x + 1)
                word.pop(x)

        word_dict = {'"': 0, "'": 0, "!": 0, "`": 0, ".": 0, "(": 0, ")": 0, "{": 0, "}": 0, "/": 0, "\\": 0, ":": 0,
                     "'s": 0, "[": 0, "]": 0, "<": 0, ">": 0, ",": 0, "‘": 0, "’": 0,"?":0}
        new_word_list = []
        new_word = ''
        for each in range(len(word)):
            if word[each] in word_dict:
                pass
            else:
                new_word += word[each]
        new_word_list.append(new_word.lower())
        for each in range(len(new_word)):
            if new_word[each] == '-':
                new_word_list.append("".join(new_word[:each]).lower())
                new_word_list.append("".join(new_word[each + 1:]).lower())
        new_word_list.append(original_word.lower())
        return list(set(new_word_list))

Main.fetch_all()
print(Search.multi_word_query("The"))

