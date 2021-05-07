from main import Bridge, RandomPlayer
import pandas as pd
import sys

bids = []
wins = []

game = Bridge(gui=True)
game.init()

#for i in range(1000):
#    sys.stdout.write('\r'+str(i))
#    game.start()
#    bids.append(game.final_bid)
#    wins.append(game.Winner)
#    sys.stdout.flush()

#print(pd.Series(bids).value_counts())
#print(pd.Series(wins).value_counts())