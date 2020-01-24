class StringOp:
    def __init__(self,data):
        self.str = data
    @classmethod
    def StrLength(cls,string):
        length = 0
        for x in string:
            length+=1
        return length

    def StrConcat(self,string1,string2):
        length1 = self.StrLength(string1)
        length2 = self.StrLength(string2)
        length3 = length1+length2
        new_string = ['' for x in range(length3)]

        for x in range(length1):
            new_string[x] = string1[x]

        for y in range(length2):
            new_string[length1+y] = string2[y]

        new_string = "".join(new_string)
        return new_string
    @classmethod
    def SubString(cls,text,start,end):
        length = cls.StrLength(text)
        new_string = ['' for x in range(start+1,end)]
        a = 0
        for x in range(start+1,end):
            new_string[a] = text[x]
            a+=1
        return "".join(new_string)

    def InsertStr(self, data, text, pos):
        length1 = self.StrLength(data)
        length2 = self.StrLength(text)
        length3 = length1+length2
        new_string = ['' for x in range(length3)]
        for x in range(pos):
            new_string[x] = data[x]

        for x in range(pos,pos+length2):
            new_string[x] = text[x-pos]
        a = 0
        for x in range(pos+length2,length3):
            new_string[x] = data[a+pos]
            a+=1

        return "".join(new_string)

    def DeleteStr(self, data, pos, length):
        length1 = self.StrLength(data)
        length2 = length1 - length
        new_string = ['' for x in range(length2)]

        for x in range(pos):
            new_string[x] = data[x]

        for x in range(pos,length2):
            new_string[x] = data[x+length]

        return "".join(new_string)
    @classmethod
    def check_pattern(cls,x,y):
        length = cls.StrLength(x)
        for a in range(length):
            if x[a]!=y[a]:
                return False
        return True

    def Naive(self, data, pattern):
        length_data    = self.StrLength(data)
        length_pattern = self.StrLength(pattern)
        indexes = []
        for x in range(length_data-length_pattern+1):
            if self.check_pattern(self.SubString(data,x-1,x+length_pattern),pattern) == True:
                # indexes.append((x,x+length_pattern-1))
                indexes.append(x)
        return indexes
    @classmethod
    def RabinKarp(cls,data,pattern,radix,prime):
        length_text = len(data)
        length_pat  = len(pattern)
        p = 0
        t = 0
        h = ((radix)**(length_pat-1))%prime
        indexes = []
        for x in range(length_pat):
            p = ((radix*p) + ord(pattern[x]))  %prime
            t = ((radix*t) + ord(data[x])) %prime

        for i in range(length_text-length_pat+1):
            if p==t:
                if cls.check_pattern(cls.SubString(data,i-1,i+length_pat),pattern) == True:
                    indexes.append(i)
            if i<length_text-length_pat:
                t = ((radix*(t-(ord(data[i])*h)))+ord(data[i+length_pat]))%prime

        return indexes

