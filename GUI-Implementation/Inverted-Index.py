import sqlite3
from string_func import *
import tkinter as tk
from tkinter import *
import time
import datetime
from tkinter import ttk
class Word:
    #Format 'word':[[doc_id,[indexes],[doc_id,[indexes]]
    words = {}
    def __init__(self,word,doc_id,indexes):
        #This function will only be used when reading data from the database
        indexes = list(map(int,indexes.split(",")))
        self.word   = word
        self.doc_id = doc_id
        self.indexes= indexes
        if self.word in Word.words:
            Word.words[self.word].append([self.doc_id,self.indexes])
        else:
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
                        if words_list[0]!= '-' or words_list[0]!= '':
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
                        if words_list[0] != '-' or words_list[0] != '':
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

        word_dict={'"':0,"'":0,"!":0,"`":0,".":0,"(":0,")":0,"{":0,"}":0,"/":0,"\\":0,":":0,"'s":0,"[":0,"]":0,"<":0,">":0,",":0,"‘":0,"’":0}
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
        # doc_name = input("Please enter the document name:")
        # doc = input("Please enter the document:")
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

        return searched_indexes

    @classmethod
    def multi_word_query(cls,user_query):
        #First Split the words in the query
        #Normalize each word for a search in our dictionary
        #create a list for each word {'doc_id','doc_id'}
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


class Interface:
    def __init__(self):
        self.loading()
        self.configure_root()

    def loading(self):
        root = Tk()
        root.geometry("630x600")
        root.title("Accounting")
        canvas = Canvas(root, width=5000, height=4000)
        canvas.pack()
        my_image = PhotoImage(file="Home_screen.png")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_height = 900
        window_width = 1500
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root.overrideredirect(True)
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        def disable_event():
            pass
        root.protocol("WM_DELETE_WINDOW", disable_event)
        Main.fetch_all()
        canvas.create_image(40,10, anchor=NW, image=my_image)
        # self.get_data()
        root.after(1000, root.destroy)
        root.mainloop()

    def configure_root(self):
        self.root = Tk()
        self.root.geometry("1300x600")
        self.root.resizable(0, 0)
        self.root.title("Inverted Index")
        window_height = 500
        window_width = 1250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.root.configure(background='powder blue')
        style = ttk.Style()
        def donothing():
            pass
        def add_doc():
            self.root.destroy()
            self.add_document()
        def single_query():
            self.root.destroy()
            self.single_word()
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_separator()
        helpmenu.add_command(label="Add document", command=add_doc)
        menubar.add_cascade(label="Add", menu=helpmenu)
        querymenu=Menu(menubar, tearoff=0)
        querymenu.add_separator()
        querymenu.add_command(label="Single word query",command=single_query)
        querymenu.add_command(label="Multiple word query", command=donothing)
        menubar.add_cascade(label="Search Engine",menu=querymenu)

        self.root.config(menu=menubar)
        self.root.mainloop()

    def add_document(self):
        root = Tk()
        root.geometry("1300x600")
        root.resizable(0, 0)
        root.title("Inverted Index")
        window_height = 700
        window_width = 1250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        root.configure(background='White')
        canvas = Canvas(root, width=1500, height=70)
        canvas.pack()
        this_image = PhotoImage(file="add_doc.png")
        canvas.create_image(0, -220, anchor=NW, image=this_image)
        doc_title=StringVar()
        doc_doc=  StringVar()
        def add():
            # title=inp_1.get("1.0","end-1c")
            title=doc_title.get()
            # doc=inp_2.get("1.0","end-1c")
            doc=doc_doc.get()
            Document.create_object(title,doc)
            root.destroy()
            self.add_document()

        Label(root,text="Enter Document Title").pack()
        inp_1=Entry(root,textvariable=doc_title,fg="black",bg="White",width=70).pack()
        Label(root,text="Enter Document").pack()
        inp_2=Entry(root,textvariable=doc_doc,fg="black", bg="white", width=70).pack()
        Button(root,fg="black", bg="white", text="ADD", height=2, width=5,command=add).pack()
        style = ttk.Style()
        frame = Frame(root)
        frame.pack()
        tree = ttk.Treeview(frame, columns=(1, 2), height=15, show="headings", style="mystyle.Treeview")
        tree.pack(side='left')
        tree.heading(1, text="Document name")
        tree.heading(2, text="Text")
        tree.column(1, width=100)
        tree.column(2, width=1100)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scroll.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scroll.set)
        lst_doc=[]
        for k,v in Document.document.items():
            tree.insert('', 'end', values=(str(v.doc_name),str(v.doc)))

        root.mainloop()
    def single_word(self):
        root = Tk()
        root.geometry("1300x600")
        root.resizable(0, 0)
        root.title("Inverted Index")
        window_height = 700
        window_width = 1250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        root.configure(background='White')
        canvas = Canvas(root, width=1500, height=250)
        canvas.pack()
        this_image = PhotoImage(file="Search.png")
        canvas.create_image(0, -220, anchor=NW, image=this_image)
        style = ttk.Style()

        def quit():
            root.destroy()
            self.configure_root()
        def go():
            # start_time = time.time()
            a=datetime.datetime.now()
            tree.delete(*tree.get_children())
            user_query=query.get()
            if Search.CountWords(user_query)==1:
                x=Search.search_single_word(user_query)
                for k, v in x.items():
                    print(k,v)
                    for all in v:
                        for m in all[1]:
                            print(Document.document[all[0]].doc[m-10:m+30])
                            tree.insert('', 'end',values=(k, "......" + str(Document.document[all[0]].doc[m:m+10]) + "...."))

                    # for a, b in v.items():
                    #     for x in b:
                    #         tree.insert('', 'end',values=(a, "......" + str(Document.document[k].doc[x - 10:x + 10]) + "...."))

            else:
                x=Search.multi_word_query(user_query)
                for k,v in x.items():
                    for a,b in v.items():
                        for x in b:
                            if x>10:
                                tree.insert('', 'end', values=(a,"......"+str(Document.document[k].doc[x-10:x+20])+"...."))
                            else:
                                tree.insert('', 'end', values=( a, "......" + str(Document.document[k].doc[0:x + 20]) + "...."))
                # tree.insert('','end',values=("--- %s seconds ---" % (time.time() - start_time),"Time Taken"))



        query=tk.StringVar()
        Entry(canvas, fg="black", bg="white", width=90, textvariable=query).place(x=360, y=140, height=40)
        Button(canvas, fg="black", bg="white", text="GO!", height=2, width=5, command=go).place(x=910, y=140)
        Button(canvas, fg="black", bg="white", text="Quit", height=2, width=5, command=quit).place(x=620, y=180)
        frame = Frame(root)
        frame.pack()
        tree = ttk.Treeview(frame, columns=(1, 2), height=40, show="headings", style="mystyle.Treeview")
        tree.pack(side='left')
        tree.heading(1, text="Document name")
        tree.heading(2, text="Passage")
        tree.column(1, width=220)
        tree.column(2, width=1000)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scroll.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scroll.set)
        root.mainloop()


Interface()



