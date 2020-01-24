# Inverted-Index-Python
Implementation of Inverted Indexes on Python.

Classes:

1) Word
    
    
    Functions:
      
      
      a) create_object(word,doc_id,indexes) - classmethod
      
      
      Description : Creates an object of the word class, saves the word in the word dictionary in the Word class.
      
      
      b) create_indexes(doc_id,doc_name,doc) - classmethod
      
      
      Description : Splits words and then creates_object of each word in the document after creating keys and indexes for each word
      
      
      c) normalize_word(word) - classmethod
      
      
      Description : Normalizes a word i.e. 'WoRd,' will be returned as word and 'RaBin-KaRp' will be returned as                                               [rabin-karp, rabin, karp]


2) Document
    
    
    Function:
      
      
      a) create_object(doc_name,doc) - classmethod
      
      
      Description : Creates a document object. Takes 2 parameters from user 'doc_name' and 'doc'.


3) Main


    Function:


      a) fetchall()


      Description : This will fetch all the data from the database and saves it in the dictionaries for searching.


4) Search


    Function:


    a)  search_single_word(user_query) - classmethod


    Description : This will search a single word and return a dictionary with the searched word with doc id and indexes.


    b)  multi_word_query(user_query) - classmethod


    Description : This will search multiple words. It searches with higher priority given to AND operator for example if a search                           query is passed "The quick brown fox" it will first try to search a document which will include all these words.                           If not then OR operator is given priority and it will return a list of documents with the most number of words                             from the search query occuring in the document. 


    c)  create_tokens(doc) - classmethod


    Description : This will seperate different words from a multiword query


    d)  normalize_word(word) - classmethod


    Description : Normalizes a word i.e. 'WoRd,' will be returned as word and 'RaBin-KaRp' will be returned as                                               [rabin-karp, rabin, karp]
         
# Functions to be used by User:-


Functions:


1) Main.fetchall()


Description : This will fetch all the data from the database so that the user can then search the word from the already saved                         documents.


2) Document.create_object(doc_name,doc)


Description : This will be used to create a document and save the words and documents in the database to be searched. The user                         needs to pass the document name and then the document itself.


3) Search.search_single_word(user_query)


Description : This will return a dictionary with the word and a list of document id and indexes in those particular documents.                         This will take a single word query.


4) Search.multi_word_query(user_query)


Description : This will return a dictionary with the word and a list of document id and indexes in those particular documents.
                    This will take a multi word query.
