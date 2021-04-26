
from tkinter import Tk, Label, Button, IntVar, DISABLED, NORMAL
from PIL import ImageTk, Image
import numpy as np
import pandas as pd
from time import sleep

class Bridge:
    def __init__(self):
        pass
    
    def get_weight(self, card_name):
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
    
    def init_main_board(self): # Create main board with shuffled cards and bidding system
        
        ### Main setup
        self.root.geometry('1200x800')
        self.bidding_scale = 0.03
        self.scale = 0.12
        self.card_path = 'cards/png1/'
        self.middle_card_path = 'cards/png1/gray_back.png'
        self.w, self.h = Image.open(self.card_path+'10C.png').size
        self.card_type = ['C', 'S', 'D', 'H'] # Club, Spade, Diamond, Heart 
        self.card_face = ['A'] + list(map(str, range(2, 10+1))) + ['J', 'Q', 'K'] # A, 1 to 10, J, Q, K
        self.card_imgs = pd.DataFrame(np.zeros((52,5))*np.nan, 
                                      columns=['id', 'type', 'scaled_img', 'img', 'face'], dtype='object')
        self.played = IntVar(self.root)
        
        # Loading all card images
        ind = 0
        for card_type in self.card_type:
            for card_face in self.card_face:
                img = Image.open(f'{self.card_path}{card_face}{card_type}.png')
                scaled_img = ImageTk.PhotoImage(img.resize((int(self.w*self.scale), int(self.h*self.scale))))
                self.card_imgs.loc[ind, 'id'] = card_face+card_type
                self.card_imgs.loc[ind, 'type'] = card_type
                self.card_imgs.loc[ind, 'face'] = card_face
                self.card_imgs.loc[ind, 'img'] = img
                self.card_imgs.loc[ind, 'scaled_img'] = scaled_img
                ind += 1
        self.card_imgs.set_index('id', inplace=True)
        
        
        ### Initialization
        self.BidTurn = -1 # To update turns
        self.bidding_array = [-1, -1, -1] # To store previous bids
        
        ### Start button
        self.StartButton = Button(self.root, text='Start/Restart', font=('Arial', 25))
        self.StartButton.place(x=0,y=0)
        self.StartButton.configure(command = self.Start)
        
        ##########################################
        ## Bidding system
        ##########################################
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
        
        global_idx = 0
        for row in range(rows):
            for column in range(columns):
                if column==0:
                    self.bidding_buttons[row, column] = Label(self.root, text=str(row+1), font=('Arial',16))
                    self.bidding_buttons[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
                else:
                    self.bidding_buttons[row, column] = Button(self.root, image=trupt_imgs[column-1])
                    self.bidding_buttons[row, column].configure(command = \
                                lambda button=self.bidding_buttons[row, column]: self.bidding_func(button))
                    self.bidding_buttons[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
                    self.bidding_buttons[row, column].id = global_idx
                    self.bidding_buttons[row, column].row = row
                    self.bidding_buttons[row, column].column = column
                    self.bidding_buttons[row, column].value = str(row+1)+'_'+trupt_names[column-1][0]
                    
                    global_idx += 1 
        
        self.PassButton = Button(self.root, text='PASS')
        self.PassButton.place(x=xoffset+column*xgap-50, y=yoffset+row*ygap+30)
        self.PassButton.value = 'PASS'
        self.PassButton.config(command = lambda button=self.PassButton: self.bidding_func(button))
        
        ##########################################
        ## Bidding Display
        ##########################################
        rows, columns = 10, 4
        xoffset, yoffset = 10, 400
        xgap = 70
        ygap = 20

        self.bidding_display = np.empty((rows,columns), dtype='object')
        self.player = ['S', 'W', 'N', 'E']
        
        for row in range(rows):
            for column in range(columns):
                if row==0:
                    self.bidding_display[row, column] = Label(self.root, text=self.player[column], font=('Arial', 14))
                    self.bidding_display[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
                else:
                    self.bidding_display[row, column] = Label(self.root, text="    ", font=('Arial', 14))
                    self.bidding_display[row, column].place(x=xoffset+column*xgap, y=yoffset+row*ygap)
        
        ##########################################
        ## Card Page 
        ##########################################
        self.card_imgs = self.card_imgs.sample(n=len(self.card_imgs), replace=False)
        
        ### Arranging cards
        # 0-13 - South
        # 13-26 - West
        # 26-39 - North
        # 39-52 - East
        
        self.Buttons = np.empty((4, 13), dtype='object')
        
        #################### Placing cards in South, West, North, East
        offset = [500, 50, 500, 50]
        gap = [30, 30, 30, 30]
        y = [500, None, 10, None]
        x = [None, 350, None, 1000]
        self.directions = ['S', 'W', 'N', 'E']
        global_id = 0
        for d_i in range(4): # d_i = direction index (S, W, N, E)
            idx = np.argsort(self.card_imgs.iloc[13*d_i:13*(d_i+1)]['type'].values)+(13*d_i)
            for i, ix in enumerate(idx):
                self.Buttons[d_i, i] = Button(self.root, image=self.card_imgs.iloc[ix]['scaled_img'])
                
                ### Setting several useful properties
                self.Buttons[d_i, i].place(x=x[d_i] if x[d_i] else offset[d_i]+gap[d_i]*i, 
                                      y=y[d_i] if y[d_i] else offset[d_i]+gap[d_i]*i)
                self.Buttons[d_i, i].name = self.card_imgs.index[ix]
                self.Buttons[d_i, i].id = global_id
                self.Buttons[d_i, i].img = self.card_imgs.iloc[ix]['scaled_img']
                self.Buttons[d_i, i].direction = self.directions[d_i]
                self.Buttons[d_i, i].weight = self.get_weight(self.Buttons[d_i, i].name)
                self.Buttons[d_i, i].played = False
                
                # Configure to call a function on clicking and return self
                button_func = lambda button=self.Buttons[d_i, i]: self.card_button_func(button)
                self.Buttons[d_i, i].configure(command = button_func)
                
                global_id += 1
        
        ### Disable all the card buttons initially
        for b in self.Buttons.ravel():
            b.config(state=DISABLED)
        
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
        self.MidLabels = []
        mimg = Image.open(self.middle_card_path)
        self.mscaled_img = ImageTk.PhotoImage(mimg.resize((int(self.w*self.scale), int(self.h*self.scale))))
        x = [650, 600, 650, 700]
        y = [300, 250, 200, 250]
        for i in range(4):
            self.MidLabels.append(Label(self.root, image=self.mscaled_img))
            self.MidLabels[i].place(x=x[i], y=y[i])
            
        ## Trick board
        self.NSTricks = 0
        self.WETricks = 0
        self.TrickDisplay = Label(self.root, text=f'Tricks:\nNS = {self.NSTricks}\nWE = {self.WETricks}', 
                                 font=("Arial", 14), bg='blue', fg='white')
        self.TrickDisplay.place(x=210, y=170)
        
        ## Result board
        self.ResultDisplay = Label(self.root, text='Complete\nthe bidding', 
                                 font=("Arial", 20), bg='black', fg='white')
        self.ResultDisplay.place(x=300, y=560)
        
        ## Bidding final board
        self.BidDisplay = Label(self.root, text='Bid Won by:  \nBid:    ', 
                                 font=("Arial", 14), bg='blue', fg='white')
        self.BidDisplay.place(x=210, y=100)
        
        self.root.mainloop()
    
    def card_button_func(self, button): # Triggered when a card is played
        self.played_button = button
        self.played.set(self.played.get()+1)
        
    def bidding_func(self, button):
        if button.value != 'PASS':
            for i in range(button.id+1):
                self.bidding_buttons[:,1:].ravel()[i].config(state=DISABLED)
        self.bidding_array.append(button.value)
        
        if set(self.bidding_array[-3:]) == set(['PASS']):
            for b in self.bidding_buttons.ravel():
                b.config(state=DISABLED)
                self.PassButton.config(state=DISABLED)
            self.final_bid = self.bidding_array[-4]
            self.trump = self.bidding_array[-4].split('_')[-1]
            self.BidWinner = (self.BidTurn+2)%4
            self.current_player = (self.BidTurn+3)%4
            self.BidDisplay.config(text=f'Bid Won by: {self.player[self.current_player-1]}\nBid: {self.final_bid}')
            self.ResultDisplay.config(text='Game is\nON')
            self.bidding_display.ravel()[len(self.bidding_array)].config(text=button.value)
            return self.game_play()
        
        self.BidTurn = (self.BidTurn+1)%4
        self.bidding_display.ravel()[len(self.bidding_array)].config(text=button.value)
        
    def game_play(self):
        self.gameover = False
        self.current_suit = None
        for i in range(13): # Total 13 tricks will be played
            self.current_player = self.play_trick(self.current_player)
        
        if self.BidWinner in [0,2]:
            if self.NSTricks >= int(self.final_bid.split('_')[0])+6:
                self.ResultDisplay.config(text='NS\nWon the Game')
            else:
                self.ResultDisplay.config(text='WE\nWon the Game')
        else:
            if self.WETricks >= int(self.final_bid.split('_')[0])+6:
                self.ResultDisplay.config(text='WE\nWon the Game')
            else:
                self.ResultDisplay.config(text='NS\nWon the Game')
        
    def play_trick(self, current_player):
        self.played_cards = []
        weights = []
        players = [current_player]
        for i in range(4):
            self.enable_player(current_player)
            played_card, card_weight = self.play_move(current_player)
            
            self.played_cards.append(played_card)
            weights.append(card_weight)
            
            current_player = (current_player+1)%4
            players.append(current_player)
        
        print(weights)
        current_player = players[np.argmax(weights)]
        
        if current_player in [0,2]:
            self.NSTricks += 1
        else:
            self.WETricks += 1
        self.ResultDisplay.config(text=self.player[current_player]+'\nwon the trick')
        self.TrickDisplay.config(text= f'Tricks:\nNS = {self.NSTricks}\nWE = {self.WETricks}')
        
        return current_player
        
    def play_move(self, current_player):
        while True:
            self.root.wait_variable(self.played)
            
            if len(self.played_cards) == 0: # First player
                self.CleanMiddle()
                return self.play_card(current_player)
            else: # Non-first players
                suit = self.played_cards[0][-1]
                is_same_suit = self.played_button.name[-1] == suit
                if is_same_suit:
                    return self.play_card(current_player)
                else:
                    is_suit_available = any([button.name[-1]==suit for button in self.Buttons[current_player, :] if button['state']=='normal'])
                    if not is_suit_available:
                        if self.played_button.name[-1] == self.trump:
                            return self.play_card(current_player, extra_weight=1000)
                        else:
                            return self.play_card(current_player, extra_weight=-1000)
                    else:
                        self.ResultDisplay.configure(text='Invalid move\nTry again!')
                        continue
    
    def CleanMiddle(self):
        for label in self.MidLabels:
            label.configure(image=self.mscaled_img)
    
    def play_card(self, current_player, extra_weight=0):
        self.MidLabels[current_player].configure(image=self.played_button.img)
        self.ResultDisplay.configure(text='Next Move')
        self.played_button.configure(state=DISABLED)
        self.played_button.configure(text='Played')
        self.played_button.played = True
        return self.played_button.name, self.played_button.weight + extra_weight
    
    def enable_player(self, current_number):
        all_players = [0,1,2,3]
        all_players.remove(current_number)
        ## Disable all other players
        for idx in all_players:
            for button in self.Buttons[idx,:]:
                button.configure(state=DISABLED)
        
        ## Enable current player
        for button in self.Buttons[current_number,:]:
            if not button.played:
                button.configure(state=NORMAL)
                
    def Start(self):
        try:
            self.root.destroy()
            self.root = Tk()
        except AttributeError:
            self.root = Tk()
        self.init_main_board()
