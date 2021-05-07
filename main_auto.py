
from tkinter import Tk, Label, Button, IntVar, DISABLED, NORMAL
from itertools import cycle
from sklearn.utils import shuffle
from PIL import ImageTk, Image
import numpy as np
import pandas as pd
from time import sleep

class Bridge:
    def __init__(self, gui=True):
        self.root = Tk()
        self.gui = gui
        self.game_is_initialized = False
    
    def start(self): # Restarts the game without initializing basic blocks
        print('Game start')
        #### Bidding system (Non-gui)
        self.last_bid = None
        self.bidding_array = ["-1_-1","-1_-1","-1_-1"]
        self.NSTricks = 0
        self.WETricks = 0
        if self.gui:
            self.reset_bidding_gui()
        
        #### Suffle the cards and assign to each player
        for b in self.Buttons.ravel():
            b.config(state=NORMAL)
        self.card_df['played'] = False
        self.card_df = shuffle(self.card_df)
        sorted_dfs = []
        for i in range(4):
            tmp_df = self.card_df.iloc[13*i:13*(i+1)]
            sorted_dfs.append(tmp_df.sort_values('suit'))
#             print("player",i,sorted_dfs[-1].index)
        self.card_df = pd.concat(sorted_dfs)
        
        self.card_df['player'] = [self.player[0]]*13 + [self.player[1]]*13 + [self.player[2]]*13 + [self.player[3]]*13
#         print(self.card_df)
        if self.gui:
            self.reset_card_gui()
        
        #### Start bidding

        self.start_bidding()
        
        #### Start game play
        if self.gui:
            self.ResultDisplay.config(text='Game\nis\nON')
        self.start_game_play()
    
    def reset_bidding_gui(self):
        for b in self.bidding_buttons.ravel():
            b.config(state=NORMAL)
            self.PassButton.config(state=NORMAL)
        
        for b in self.bidding_display.ravel()[4:]:
            b.config(text='   ')
        
        self.BidDisplay.config(text=f'Bid Won by: \nBid: ')
        self.ResultDisplay.config(text='Complete\nthe bidding')
        self.TrickDisplay.config(text= f'Tricks:\nNS = {self.NSTricks}\nWE = {self.WETricks}')
        
    def reset_card_gui(self):
        self.clean_middle()
        for b in self.Buttons.ravel():
            b.config(state=DISABLED)
        for d_i, player in enumerate(self.player):
            for i in range(13):
                self.Buttons[d_i, i].config(image=self.card_df.iloc[13*d_i+i]['img'])
    
    def start_bidding(self):
        self.bid_players = cycle(self.agents)
        while set(self.bidding_array[-3:]) != set(['pass']) or self.last_bid is None:
#             print('lstbid',self.last_bid,'barray',self.bidding_array[-3:])
            if self.gui:
                self.root.wait_variable(self.next_var)
            bid, bid_idx = next(self.bid_players).play_bid(self.last_bid)
            
            if bid != "pass":
                self.last_bid = bid
            
            self.bidding_array.append(bid)
            
            if self.gui:
                self.update_bidding_gui(bid, bid_idx)
        
        self.final_bid = self.bidding_array[-4]
        self.trump = self.bidding_array[-4][-1]
        base_idx = len(self.bidding_array)

        # If a suit is bided by parter first, he gets the chance unless bid in "NT" (No Trump)
        if self.bidding_array[-4][-1] == self.bidding_array[-6][-1] and self.bidding_array[-4][-2:] != 'NT':
            self.BidWinner = self.player[(base_idx+3)%4]
            self.bid_winner_idx = (base_idx+3)%4
            self.current_player = (base_idx+4)%4
        else:
            self.BidWinner = self.player[(base_idx+1)%4]
            self.bid_winner_idx = (base_idx+1)%4
            self.current_player = (base_idx+2)%4
        
        print('BidWinner',self.BidWinner)
        print('Final bid',self.final_bid)
        if self.gui:
            self.finish_bidding_gui()
            
    def update_bidding_gui(self, bid, bid_idx):
        self.bidding_display.ravel()[len(self.bidding_array)].config(text=bid)
        if bid != 'pass':
            for i in range(bid_idx+1):
                self.bidding_buttons[:,1:].ravel()[i].config(state=DISABLED)
    
    def finish_bidding_gui(self):
        for b in self.bidding_buttons.ravel():
            b.config(state=DISABLED)
            self.PassButton.config(state=DISABLED)
        
        self.BidDisplay.config(text=f'Bid Won by: {self.BidWinner}\nBid: {self.final_bid}')
        self.ResultDisplay.config(text='Complete\nthe bidding')
        
    def start_game_play(self):
        self.agents[self.current_player-1].declarer = True
        
        for i in range(13): # play 13 tricks
            table = []
            player_idx = [idx%4 for idx in range(self.current_player, self.current_player+4)]
            for j in player_idx:
                cards = self.card_df.iloc[j*13:(j+1)*13]
                unplayed_cards = cards[cards['played']==False].index
                
                if self.gui:
                    self.root.wait_variable(self.next_var)
                if j == self.current_player:
                    self.clean_middle()
                
                played_card = self.agents[j].play_move(unplayed_cards, table)
                self.card_df.loc[played_card, 'played'] = True
                table.append(played_card)
                
                print(f'{played_card}', end=' ')
                if self.gui:
                    self.update_card_gui(played_card)
            
            print()
            self.current_player = player_idx[self.argbest(table)]
            if self.current_player in [0,2]:
                self.NSTricks += 1
            else:
                self.WETricks += 1
            if self.gui:
                self.update_tricks_gui()
        # Deside who won the game
        if self.bid_winner_idx in [0,2]:
            if self.NSTricks >= int(self.final_bid.split('_')[0])+6:
                self.Winner = 'NS'
            else:
                self.Winner = 'WE'
        else:
            if self.WETricks >= int(self.final_bid.split('_')[0])+6:
                self.Winner = 'WE'
            else:
                self.Winner = 'NS'
                
        print('NS tricks',self.NSTricks)
        print('WE tricks',self.WETricks)
        print('Winner is', self.Winner)
        if self.gui:
            self.ResultDisplay.config(text=f'{self.Winner}\nWon the Game')
    
    def argbest(self, table):
        weights = [self.get_weight(table[0])]
        suit = table[0][-1]
        for card in table[1:]:
            if card[-1] == suit:
                weights.append(self.get_weight(card))
            else:
                if card[-1] == self.trump:
                    weights.append(self.get_weight(card)+1000)
                else:
                    weights.append(self.get_weight(card)-1000)
        
        return np.argmax(weights)
    
    def update_tricks_gui(self):
        self.ResultDisplay.config(text=self.player[self.current_player]+'\nwon the trick')
        self.TrickDisplay.config(text= f'Tricks:\nNS = {self.NSTricks}\nWE = {self.WETricks}')
    
    def update_card_gui(self, played_card):
        idx = self.card_df.index.get_loc(played_card)
        self.Buttons.ravel()[idx].config(image=self.mscaled_img)
        self.MidLabels[idx//13].config(image=self.card_df['img'].iloc[idx])
        
    def init(self): # One time initialization
        ############## Main line of code. Set who all are playing this game
        self.agents = [RandomPlayer() for _ in range(4)]
        
        ###############################################
        # Non-gui components
        ###############################################
        self.card_df = pd.DataFrame(np.zeros((52,6))*np.nan, 
                                      columns=['id', 'suit', 'face', 'img', 'player', 'played'], dtype='object')
        self.card_type = ['C', 'S', 'D', 'H'] # Club, Spade, Diamond, Heart 
        self.player = ['S', 'W', 'N', 'E'] # South, West, North, East
        self.card_face = ['A'] + list(map(str, range(2, 10+1))) + ['J', 'Q', 'K'] # A, 1 to 10, J, Q, K
        
        ###############################################
        # gui components
        ###############################################
        self.root.geometry('1200x800')
        self.bidding_scale = 0.03
        self.scale = 0.12
        self.card_path = 'cards/png1/'
        self.middle_card_path = 'cards/png1/gray_back.png'
        self.w, self.h = Image.open(self.card_path+'10C.png').size
        mimg = Image.open(self.middle_card_path)
        self.mscaled_img = ImageTk.PhotoImage(mimg.resize((int(self.w*self.scale), int(self.h*self.scale))))
        self.played = IntVar(self.root)
        self.next_var = IntVar(self.root)
        
        # Loading all card images (gui)
        ind1 = 0
        for card_type in self.card_type:
            for card_face in self.card_face:
                img = Image.open(f'{self.card_path}{card_face}{card_type}.png')
                scaled_img = ImageTk.PhotoImage(img.resize((int(self.w*self.scale), int(self.h*self.scale))))
                self.card_df.loc[ind1, 'id'] = card_face+card_type
                self.card_df.loc[ind1, 'suit'] = card_type
                self.card_df.loc[ind1, 'face'] = card_face
                self.card_df.loc[ind1, 'img'] = scaled_img
                ind1 += 1
        self.card_df.set_index('id', inplace=True)
        
        ### Start button (gui)
        self.StartButton = Button(self.root, text='Start/Restart', font=('Arial', 25))
        self.StartButton.place(x=0,y=0)
        self.StartButton.configure(command = self.start)
        
        ### Next button (gui)
        self.NextButton = Button(self.root, text='Next', font=('Arial', 25))
        self.NextButton.place(x=0,y=50)
        def inc_robo_play():
            self.next_var.set(self.next_var.get()+1)
        self.NextButton.configure(command = inc_robo_play)
        
        ### Bidding system (gui)
        rows, columns = 7, 6
        xoffset, yoffset = 10, 100
        xgap = 30
        ygap = 40
        w, h = Image.open(self.card_path+'NT.png').size
        trupt_names = ['Club', 'Diamond', 'Heart', 'Spade', 'NT']
        trupt_imgs = [Image.open(self.card_path+name+'.png') for name in trupt_names]
        trupt_imgs = [ImageTk.PhotoImage(img.resize((int(w*self.bidding_scale), 
                                               int(h*self.bidding_scale)))) for img in trupt_imgs]

        self.bidding_buttons = np.empty((rows,columns), dtype='object')
        
        ind2 = 0
        for row in range(rows):
            for column in range(columns):
                if column==0:
                    self.bidding_buttons[row, column] = Label(self.root, text=str(row+1), font=('Arial',16))
                    self.bidding_buttons[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
                else:
                    self.bidding_buttons[row, column] = Button(self.root, image=trupt_imgs[column-1])
                    self.bidding_buttons[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
        
        self.PassButton = Button(self.root, text = 'pass')
        self.PassButton.place(x=xoffset+column*xgap-50, y=yoffset+row*ygap+30)
        
        ##########################################
        ## Bidding Display (gui)
        ##########################################
        rows, columns = 10, 4
        xoffset, yoffset = 10, 400
        xgap = 70
        ygap = 20

        self.bidding_display = np.empty((rows,columns), dtype='object')
        
        for row in range(rows):
            for column in range(columns):
                if row==0:
                    self.bidding_display[row, column] = Label(self.root, text=self.player[column], font=('Arial', 12))
                    self.bidding_display[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
                else:
                    self.bidding_display[row, column] = Label(self.root, text="    ", font=('Arial', 12))
                    self.bidding_display[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
                    
        ##############################
        # Cards display (gui)
        ##############################
        
        self.Buttons = np.empty((4, 13), dtype='object')
        
        #################### Placing cards in South, West, North, East
        offset = [500, 50, 500, 50]
        gap = [30, 30, 30, 30]
        y = [500, None, 10, None]
        x = [None, 350, None, 1000]

        for d_i in range(4): # d_i = direction index (S, W, N, E)
            idx = np.argsort(self.card_df.iloc[13*d_i:13*(d_i+1)]['suit'].values)+(13*d_i)
            for i, ix in enumerate(idx):
                self.Buttons[d_i, i] = Button(self.root, image=self.card_df.iloc[ix]['img'])
                
                ### Setting several useful properties
                self.Buttons[d_i, i].place(x=x[d_i] if x[d_i] else offset[d_i]+gap[d_i]*i, 
                                      y=y[d_i] if y[d_i] else offset[d_i]+gap[d_i]*i)
                self.Buttons[d_i, i].img = self.mscaled_img
                
                # Configure to call a function on clicking and return self
                button_func = lambda button=self.Buttons[d_i, i]: self.card_button_func(button)
                self.Buttons[d_i, i].configure(command = button_func)
        
        ### Labeling four directions
        S = Label(text='S', bg='red', fg='white', font=('Arial', 22))
        N = Label(text='N', bg='red', fg='white', font=('Arial', 22))
        W = Label(text='W', bg='red', fg='white', font=('Arial', 22))
        E = Label(text='E', bg='red', fg='white', font=('Arial', 22))
        S.place(x=offset[0]+gap[0]*6.5, y=y[0]-50)
        N.place(x=offset[2]+gap[2]*6.5, y=y[2]+140)
        W.place(x=x[1]+100, y=offset[1]+gap[1]*6.5)
        E.place(x=x[3]-30, y=offset[3]+gap[3]*6.5)
        
        ## Placing four cards in the middle
        self.MidLabels = [None, None, None, None]
        x = [650, 600, 650, 700]
        y = [300, 250, 200, 250]
        for i in range(4):
            self.MidLabels[i] = Label(self.root, image=self.mscaled_img)
            self.MidLabels[i].place(x=x[i], y=y[i])
            
        ## Trick board
        self.NSTricks = 0
        self.WETricks = 0
        self.TrickDisplay = Label(self.root, text=f'Tricks:\nNS = {self.NSTricks}\nWE = {self.WETricks}', 
                                 font=("Arial", 14), bg='blue', fg='white')
        self.TrickDisplay.place(x=210, y=170)
        
        ## Result board
        self.ResultDisplay = Label(self.root, text='Press Start', 
                                 font=("Arial", 20), bg='black', fg='white')
        self.ResultDisplay.place(x=300, y=560)
        
        ## Bidding final board
        self.BidDisplay = Label(self.root, text='   ', 
                                 font=("Arial", 14), bg='blue', fg='white')
        self.BidDisplay.place(x=210, y=100)
        
        self.game_is_initialized = True
        
        self.root.mainloop()
    
    def clean_middle(self):
        for label in self.MidLabels:
            label.configure(image=self.mscaled_img)
    
    def get_weight(self, card_name): # Get pure weights of cards 2-3---13-14 -> 2-3---K-A
        if card_name[0] == 'J':
            return 11
        elif card_name[0] == 'Q':
            return 12
        elif card_name[0] == 'K':
            return 13
        elif card_name[0] == 'A':
            return 14
        else:
            return int(card_name[:-1])

class RandomPlayer:
    def __init__(self, declarer=False):
        self.type_dict = {c:i for i,c in enumerate(['C', 'D', 'H', 'S', 'NT'], 1)}
        self.bid_types = ['C', 'D', 'H', 'S', 'NT']
        self.card_proba = 1/np.arange(1,8).reshape(-1,1).repeat(5,1)**2 # Descreasing probabilities of bidding higher
        self.pass_proba = 10
        self.declarer = declarer
        
    def play_bid(self, last_bid):
        bid_idx=None
        if last_bid is not None:
            last_card, last_type = last_bid.split('_')
            begin_idx = (int(last_card)-1)*5 + self.type_dict[last_type]
            all_proba = np.array([self.pass_proba] + self.card_proba.ravel().tolist()[begin_idx:])
        else:
            begin_idx = 0
            all_proba = np.array([self.pass_proba] + self.card_proba.ravel().tolist())
        
        norm_all_proba = all_proba/np.sum(all_proba)
        choice = np.random.choice(len(norm_all_proba), p=norm_all_proba, size=1)[0]
        
        if choice == 0:
            bid = 'pass'
        else:
            bid_idx = begin_idx + choice - 1
            bid = str(bid_idx//5+1) +'_'+ self.bid_types[bid_idx%5]
        
        return bid, bid_idx
            
    def play_move(self, cards, table, dummy_cards=None):
        if self.declarer:
            if len(table) == 0:
                return np.random.choice(cards)
            suit = table[0][-1]
            same_suit_cards = [card for card in cards if card[-1]==suit]
            if len(same_suit_cards)==0:
                return np.random.choice(cards)
            else:
                return np.random.choice(same_suit_cards)
        else:
            if len(table) == 0:
                return np.random.choice(cards)
            suit = table[0][-1]
            same_suit_cards = [card for card in cards if card[-1]==suit]
            if len(same_suit_cards)==0:
                return np.random.choice(cards)
            else:
                return np.random.choice(same_suit_cards)
