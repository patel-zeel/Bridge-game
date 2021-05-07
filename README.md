# Bridge-game

```main_auto.py``` and ```main_manual.py``` have the main classes of the game.

Basic usage is given below,

### For manual bidding and game-play
```python
from main_manual import Bridge

game = Bridge()
game.init()
```

### For automatic bidding and game-play
```python
from main_auto import Bridge

game = Bridge()
game.init() # Starts the GUI if GUI=True else solves one random game on its own. 
