# Dominion
This is a simple scripting practice project that allows users to play a text-based approximation of Donald X. Vaccarino's card game Dominion. It assumes knowledge of the rules of Dominion.

# Playing the game
Unmodified, the script when run will start a new game and prompt the user to add players and kingdoms. I recommend 2-4 players and a random choice of kingdoms. All players are human-controlled (computer players coming soon!) 

To view card descriptions, enter "help" at any prompt. 

Inputs are not case-sensitive. 

# Features and program description
The game currently implements 13 Kingdom cards (all from the Dominion base set) in addition to the basic treasure, victory, and curse cards. A goal was to make the code modular and extensible. It will be straightforward to add rule-based AI players on top of the existing code, for example. 

The structure is as follows. A Game object handles startup, tracking the gamestate, running the main game loop, and exiting. The main game loop calls the take_turn method of each of the Player objects until the game-over state is met (Province pile empty or 3 Kingdom piles empty). The take_turn method loops through the phases of the turn: action, buy, and cleanup, each of which is implemented through methods of the Player object. Most player game actions (drawing/reshuffling, resource tracking, buying, cleanup, etc.) are also implemented in Player methods. Action cards are played via passing the player and game objects to the resolve method of the appropriate Card object, which carries out the card instructions and returns the modified player and game objects. 

The game uses the Shelve library to save and load games. 
