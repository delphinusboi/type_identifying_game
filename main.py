#!./bin/python3.11

import os
import sqlite3
import hashlib
import random
import datetime # make sure we have the right datetime
import string
#import tkinter # maybe not tkinter.

score_database = "./score_database.db"

# determine if the score database has existed
newdb = os.path.exists(score_database)
# establish the connection to the database
conn = sqlite3.connect(score_database)

if newdb is False:
    conn.execute("CREATE TABLE player_scores(player_id text,player_name text,player_score int, date_set text, longest_streak int)")
    conn.commit()
    conn.execute("INSERT INTO player_scores(player_id,player_name,player_score,date_set,longest_streak) VALUES('%s','BATMAN',359100, '%s', 69)"%(hashlib.sha256(bytes('BATMAN','UTF-8')).hexdigest(),datetime.datetime.now().strftime("%D %T")))
    conn.commit()
    
def fixed_width(data,width=20,padding=" "):
    data = str(data)
    while len(data)<width:
        data = padding+data
    return data[:20]

def update_scoreboard():
    """
    scoreboard function - call this to update the scores.
    """
    scoreboard_cursor = conn.execute("SELECT player_name,player_score,date_set,longest_streak from player_scores ORDER BY player_score DESC")
    scoreboard = []
    record = scoreboard_cursor.fetchone()
    while len(scoreboard)<10 and record is not None:
        p_name,p_score,d_set,l_streak = record
        scoreboard.append("%s%s%s%s"%(fixed_width(p_name),fixed_width(p_score),fixed_width(l_streak),fixed_width(d_set)))
        record = scoreboard_cursor.fetchone()
    for i in range(0,40): print("")
    for i in range(0,3): print(fixed_width("=",80,"="))
    columns = ['Rank','Player Name','Score','Streak','Score Set']
    header = ""
    for col in columns: header+=fixed_width(col)
    print(header)
    for i in scoreboard:
        print("#%s%s"%(fixed_width(scoreboard.index(i)),i))
    print(fixed_width("=",80,"="))
    return scoreboard



class Player:
    def __init__(self,*args):
        self.name = fixed_width(input("Please enter your name to keep your score: ").replace("'",''))
        self.id = hashlib.sha256(bytes(self.name,'utf-8')).hexdigest()
        self.score = 0;
        self.streak = 0;
        self.new_player = conn.execute("SELECT COUNT(player_name) FROM player_scores WHERE player_id = '%s'"%(self.id)).fetchone()[0]==0
        self.lives = 3
        
    def time(self):
        return datetime.datetime.now().strftime("%D %T")
    
    def save_score(self):
        if self.new_player==True:
            conn.execute("INSERT INTO player_scores(player_id,player_name,player_score,date_set,longest_streak) VALUES('%s','%s',%s, '%s', %s)"%(self.id,self.name,self.score,self.time(),self.streak))
            print("YOUR FIRST SCORE HAS BEEN RECORDED")
            conn.commit()
        else:
            old_score = conn.execute("SELECT player_score from player_scores WHERE player_id = '%s'"%(self.id)).fetchone()[0]
            if self.score > old_score:
                conn.execute("UPDATE player_scores SET player_score=%s,date_set='%s' WHERE player_id = '%s'"%(self.score,self.time(),self.id))
                print("CONGRATULATIONS, YOU BEAT YOUR OLD HIGH SCORE!")
            conn.commit()
        #print(conn.execute("SELECT * FROM player_scores").fetchall())
    
    def right_answer(self):
        self.streak+=1
        self.score+=(150*self.streak)
        print(fixed_width('-',80,'-'))
        print(fixed_width("CORRECT!",20))
        print(fixed_width('-',80,'-'))
        print("New Score: "+fixed_width(self.score,15))
        print("New Streak: "+fixed_width(self.streak,14))
        return
    
    def wrong_answer(self):
        self.streak = 0
        print(fixed_width('-',80,'-'))
        print(fixed_width("WRONG!",20))
        print(fixed_width('-',80,'-'))
        print("New Score: "+fixed_width(self.score,15))
        print("New Streak: "+fixed_width(self.streak,14))
        self.lives -=1
        return


# game initialization
easy_mode = True;
type_set = [str,int,bool,type,dict,list,zip,tuple]
if easy_mode: type_set=[str,int,bool,list]
if easy_mode: type_set=[str,int,bool]
string_examples = [string.printable,string.ascii_lowercase,string.ascii_uppercase,str(str),"'cat'","'dog'","'animal'",'"STRING"']
integer_examples = []
boolean_examples = [True,False]
list_examples = []
dictionary_examples = [{"mammals":["dog","cat","hippo","human"]},{"integers":list(string.digits)},{
    str:string_examples,
    int:integer_examples,
    bool: boolean_examples,
    list: list_examples
}]

for i in range(0,random.randint(1,random.randint(0,100000))):
    integer_examples.append(random.randint(0,random.randint(0,100000)))
    
for i in range(0,1000):
    my_slice_index = string.printable.index(random.choice(string.printable))
    if my_slice_index > len(string.printable): my_slice_index = len(string.printable)
    if my_slice_index == 1: my_slice_index = 2
    list_examples.append(list(string.printable[:my_slice_index] ))

question_routing = {
    str:string_examples,
    int:integer_examples,
    bool: boolean_examples,
    list: list_examples,
    dict: dictionary_examples
}

update_scoreboard()
input("PRESS ENTER TO PLAY or CTRL+C TO QUIT")

# need to work on the scoreboard system - it's not quite there yet.
player = Player() # initialize the player

# getting into the main loop
while player.lives > 0:
    #match_me = random.choice(type_set) # this actually grabs a type, which can be used directly.
    match_type = random.choice(type_set)
    match_me = random.choice(question_routing[match_type])
    value = input("Please tell me what the type of this data is: %s: %s "%(match_type,match_me))
    
    try:
        if value in str(match_type) and value != "": 
            player.right_answer()
        else:
            player.wrong_answer()
    except Exception as E:
        # print E to test - we'll then go through and use this capture to pipe the output to "wrong"
        print(E)
        player.wrong_answer()

#print("GAME OVER")
# game over, cleanup down here.
player.save_score()
update_scoreboard()
print(fixed_width("--GAME OVER--",42))


