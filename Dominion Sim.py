# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 13:08:56 2020

@author: NNicholson
"""
import random

class Save_Folder:
    def __init__(self):
        self.saved_games = {}
        
    def save(self,game_name, savefile):
        self.saved_games[game_name] = savefile
    
class Save_File:
    def __init__(self,game_name,card_dict,board_state,players):
        self.game_name = game_name
        self.card_dict = card_dict
        self.board_state = board_state
        self.players = players
    
    
class Game:
    def __init__(self,game_name,card_dict,board_state,players,save_folder):
        self.game_name = game_name
        self.card_dict = card_dict
        self.board_state = board_state
        self.players = players
        self.save_folder = save_folder
        self.player_names = []
        self.running = True
        
    def input_handler(self,prompt,allowables):
        allowables += ['help','quit']
        text = input(prompt).lower()
        if text not in allowables:
            print('Invalid entry, try again.')
            return self.input_handler(prompt,allowables)
        if text == 'help':
            command = ''
            while command != 'done':
                command = self.input_handler('Enter a card name for information or enter Done to return to the game: ',[key for key in self.card_dict.keys()] + ['done'])
                if command == 'done':
                    break
                else:
                    print(self.card_dict[command].get_info())
            return self.input_handler(prompt,allowables)
        else:
            return text
        
    def new_game(self):
        if self.players == []:
            command = ''
            while command.lower() != 'stop':
                command = input('Enter a player name, or enter stop to finish entering players: ')
                if command.lower() == 'stop':
                    break
                if command == '':
                    print('Must enter a name (can be anything)')
                    return self.new_game()
                self.player_names.append(command)
            self.players = [Player(name,[],[],[]) for name in self.player_names]        
        self.play_game()
        
    def load_game(self,savefile):
        print('Game loaded from file')
        self.running = True
        self.game_name = savefile.game_name
        self.card_dict = savefile.card_dict
        self.board_state = savefile.board_state
        self.players = savefile.players
        self.play_game(True)        
    
    def play_game(self,from_save = False):
        print(str('Welcome to Dominion! \nPlayers: '+', '.join([player.name for player in self.players])+'\nEnter Help at any time to get card text.'))
        if from_save == False:
            for player in self.players:
                player.set_starting_deck()
                player.draw(5)
                #player.hand.append(Vassal())
                #player.hand.append(Throne_Room())
                #player.hand.append(Chapel())
                #player.hand.append(Moat())
                #player.hand.append(Moat())
                #player.deck.insert(0,Witch())
        while self.running:
            self.save_folder.save(self.game_name,Save_File(self.game_name, self.card_dict, self.board_state, self.players))
            print('Game saved')
            for player in self.players:
                if self.input_handler('Continue? Enter Y to keep playing or N to quit: ',['y','n'])=='n':
                    self.running = False
                    print('Game ended')
                    break
                print(player.take_turn(self.board_state,self))
                if self.game_over():
                    self.running = False
                    print(self.end())
                    break
                
    def game_over(self):
        return sum(1 for x in self.board_state.supply.values() if x <= 0) >= 3 or self.board_state.supply['Province'] <= 0
    
    def end(self):
        for player in self.players:
            player.VictoryPoints = sum(card.victory_value for card in player.hand) + sum(card.victory_value for card in player.deck) + sum(card.victory_value for card in player.discard_pile)
        self.winnerlist = sorted([player for player in self.players],key = lambda player:player.VictoryPoints,reverse = True)
        return str('Game over. '+self.winnerlist[0].name+' wins with '+str(self.winnerlist[0].VictoryPoints)+' victory points.')
        

class Card:
    def __init__(self):
        self.victory_value = 0
        self.coin_value = 0
        self.cost = 0
        self.name = ''
        self.type = []
        self.description = ''
                
    def resolve(self):
        pass
    def __repr__(self):
        return self.name
    def get_info(self):
        return ' ' + self.name +'\n Type: ' +', '.join([type for type in self.type])+'\n Cost: '+str(self.cost)+ '\n Description: '+self.description

class Copper(Card):
    def __init__(self):
        Card.__init__(self)
        self.coin_value = 1
        self.name = 'Copper'
        self.type = ['Treasure']
        self.description = 'Treasure worth 1 coin'
        
class Curse(Card):
    def __init__(self):
        Card.__init__(self)
        self.name = 'Curse'
        self.type = ['Curse']
        self.victory_value = -1
        self.description = 'Junk worth -1 victory points'

class Silver(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.coin_value = 2
        self.name = 'Silver'
        self.type = ['Treasure']
        self.description = 'Treasure worth 2 coins'
        
class Gold(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 6
        self.coin_value = 3
        self.name = 'Gold'
        self.type = ['Treasure']
        self.description = 'Treasure worth 3 coins'
        
class Estate(Card):
    def __init__(self):
        Card.__init__(self)
        self.victory_value = 1
        self.name = 'Estate'
        self.type = ['Victory']
        self.description = 'Victory card worth 1 victory point'
 
        
class Duchy(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.victory_value = 3
        self.name = 'Duchy'
        self.type = ['Victory']
        self.description = 'Victory card worth 5 victory points'
        
class Province(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 8
        self.victory_value = 6
        self.name = 'Province'
        self.type = ['Victory']
        self.description = 'Victory card worth 8 victory points'

class Cellar(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 2
        self.name = 'Cellar'
        self.type = ['Action']
        self.description = '+1 Action. Discard any number of cards, then draw that many cards.'
        self.cards_discarded = 0
        
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        self.cards_discarded = 0
        command = ''
        while command != 'stop':
            print(player.name,'\'s hand is:',[card for card in player.hand])
            command = game.input_handler(str(player.name+', enter a card to discard, or enter stop if finished: '),[key for key in game.card_dict]+['stop'])
            if command == 'stop':
                continue
            if sum(card.name.lower() == command for card in player.hand) == 0:
                print('No such card in hand, try again')
                continue
            if len(player.hand) > 0:
                for i in range(len(player.hand)):
                    if player.hand[i].name.lower() == command:
                        print(player.name,'discards a',player.hand[i].name)
                        player.discard_pile.append(player.hand.pop(i))
                        self.cards_discarded +=1
                        break
            else:
                print('No more cards in hand to discard')
                break
        player.draw(self.cards_discarded)
        return board_state, game
    
class Chapel(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 2
        self.name = 'Chapel'
        self.type = ['Action']
        self.description = 'Trash up to 4 cards from your hand.'
        self.cards_trashed = 0
        
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        self.cards_trashed = 0
        command = ''
        while command != 'stop' and self.cards_trashed < 4:
            print(player.name,'\'s hand is:',[card for card in player.hand])
            command = game.input_handler(str(player.name+', enter a card to trash, or enter stop if finished: '),[key for key in game.card_dict]+['stop'])
            if command == 'stop':
                continue
            if sum(card.name.lower() == command for card in player.hand) == 0:
                print('No such card in hand, try again')
                continue
            if len(player.hand) > 0:
                for i in range(len(player.hand)):
                    if player.hand[i].name.lower() == command:
                        print(player.name,'trashes a',player.hand[i].name)
                        board_state.trash_pile.append(player.hand.pop(i))
                        self.cards_trashed += 1
                        break
            else:
                print('No more cards in hand to trash')
                break
        print(player.name,'finished resolving',self.name)
        player.actions_remaining -= 1
        return board_state, game
    
class Council_Room(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.name = 'Council Room'
        self.type =['Action']
        self.description = '+4 cards, +1 buy. Each other play draws a card.'
    
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        player.draw(4)
        player.buys_remaining += 1
        for person in game.players:
            if person.name != player.name:
                person.draw(1)
        player.actions_remaining -= 1
        return board_state, game

class Market(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.name = 'Market'
        self.type = ['Action']
        self.description = '+1 card, +1 action, +1 buy, +1 coin.'
    
    def resolve(self,player, board_state, game):
        print(player.name,'plays a',self.name)
        player.draw(1)
        player.buys_remaining += 1
        player.coins_elsewhere += 1
        return board_state,game

class Moat(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 2
        self.name = 'Moat'
        self.type = ['Action','Reaction']
        self.description = '+2 cards. Whenever another player plays an attack card, you may reveal this to be unaffected by the attack.'

    def trigger(self,owning_player,attacking_player,attack,game):
        print('Hey ',owning_player.name,',',attacking_player.name,'is playing a ',attack.name,'!. Reveal Moat to nullify the attack against you?',sep = '')
        command = game.input_handler('Enter Y or N: ',['y','n'])
        if command == 'y':
            print(owning_player.name,'reveals a',self.name,'and is unaffected by',attack.name,'.')
            return True
        else:
            print(owning_player.name,'declines to reveal',self.name)
            return False
        
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        player.draw(2)
        player.actions_remaining -= 1
        return board_state,game
        
class Moneylender(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 4
        self.name = 'Moneylender'
        self.type = ['Action']
        self.description = 'You may trash a Copper from your hand for 3 coins.'
        
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        if sum(card.name == 'Copper' for card in player.hand) > 0:
            command = game.input_handler('Trash a Copper for 3 coins? Enter Y or N:',['y','n'])
            if command == 'y':
                player.coins_elsewhere += 3
                print(player.name, 'trashed a Copper for 3 coins.')
                for i in range(len(player.hand)):
                    if player.hand[i].name == 'Copper':
                        board_state.trash_pile.append(player.hand.pop(i))
                        break
        else:
            print('No coppers in hand, nothing to trash')                
        player.actions_remaining -= 1
        return board_state, game

class Smithy(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 4
        self.name = 'Smithy'
        self.type = ['Action']
        self.description = '+3 cards.'
        
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        player.draw(3)
        player.actions_remaining -= 1
        return board_state, game
    
class Throne_Room(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 4
        self.name = 'Throne Room'
        self.type = ['Action']
        self.description = 'You may play an action card from your hand twice.'
        
    def resolve(self,player,board_state,game):
        print(player.name,' plays a',self.name)
        player.actions_remaining -= 1
        command = ''
        while command != 'skip':
            if sum('Action' in card.type for card in player.hand) > 0:
                print('Actions in hand:',[card for card in player.hand if 'Action' in card.type])
                command = game.input_handler(str(player.name+', enter a card to play twice, or enter skip to cancel: '),[key for key in game.card_dict]+['skip'])
                if command == 'skip':
                    continue
                if sum(card.name.lower() == command for card in player.hand) == 0:
                    print('No such card in hand, try again')
                    continue
                if len(player.hand) > 0:
                    for i in range(len(player.hand)):
                        if player.hand[i].name.lower() == command:
                            player.actions_remaining += 2
                            player.play_area.append(player.hand.pop(i))
                            board_state, game = game.card_dict[command].resolve(player, board_state, game)
                            board_state, game = game.card_dict[command].resolve(player, board_state, game)
                            break
                    break
            else:
                print('No actions in hand, nothing to',self.name)
                break
        return board_state, game

class Vassal(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Vassal'
        self.type = ['Action']
        self.description = '+2 coins. Discard the top card of your deck. If it\'s an action card, you may play it.'
        
    def resolve(self,player,board_state,game):
        print(player.name,' plays a',self.name)
        target = player.deck[0]
        print(player.name,'discards a',target.name)
        if 'Action' in target.type:
            command = game.input_handler(str('Play the discarded '+target.name+'? Enter Y or N: '),['y','n'])
            if command == 'y':
                player.play_area.append(player.deck.pop(0))
                board_state, game = target.resolve(player, board_state, game)
            else:
                player.discard_pile.append(player.deck.pop(0))
        else:
            player.discard_pile.append(player.deck.pop(0))
            
        player.coins_elsewhere += 2
        player.actions_remaining -= 1
        return board_state, game
    
class Village(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Village'
        self.type = ['Action']
        self.description = '+1 card, +2 actions.'
        
    def resolve(self,player,board_state,game):
        print(player.name,' plays a',self.name)
        player.draw(1)
        player.actions_remaining += 1
        return board_state, game

class Witch(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.name = 'Witch'
        self.type = ['Action']
        self.description = '+2 cards. Each other player gains a Curse.'
        
    def resolve(self,player,board_state,game):
        immunity = False
        print(player.name,'plays a',self.name)
        player.draw(2)
        player.actions_remaining -= 1
        for victim in game.players:
            if victim.name != player.name:
                immunity = victim.trigger_reactions(player,self,game)
                if immunity == False:
                    if board_state.supply['Curse'] > 0:
                        victim.discard_pile.append(Curse())
                        board_state.supply['Curse'] -= 1
                        print(victim.name,'gains a Curse')
                    else:
                        print('No curses remain,',victim.name,'is unaffected by Witch')
            immunity = False
        return board_state,game

class Workshop(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Workshop'
        self.type = ['Action']   
        self.description = 'Gain a card costing up to 4.'
        
    def resolve(self,player,board_state,game):
        print(player.name,'plays a',self.name)
        command = game.input_handler('Enter a card to gain, costing up to 4: ')
        while game.board_state.supply[command] <1:
            command = game.input_handler('No such card available, try again: ')
        while game.card_dict.get(command,0).cost > 4:
            command = game.input_handler('Too expensive, enter another card: ')
        
class Player:
    def __init__(self,name, hand,discard_pile, deck):
        self.VictoryPoints = 0
        self.hand = hand
        self.discard_pile = discard_pile
        self.deck = deck
        self.play_area = []
        self.name = name
        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coins_elsewhere = 0
        self.coins_spent = 0
        
    def set_starting_deck(self):
        for i in range(7): self.deck.append(Copper())
        for i in range(3): self.deck.append(Estate())
        random.shuffle(self.deck)
        
    def shuffle(self):
        random.shuffle(self.discard_pile)
        self.deck += self.discard_pile
        self.discard_pile = []
        
    def draw(self,number_of_cards):
        for i in range(number_of_cards):
            if len(self.deck) + len(self.discard_pile) == 0:
                print('No cards left, you drew your deck!')
            else:
                if len(self.deck) == 0:
                    print("Out of cards, shuffling")
                    self.shuffle()
                print(self.name,'draws a card')
                self.hand.append(self.deck.pop(0))
            
    def discard(self):
        self.discard_pile += self.hand
        self.discard_pile += self.play_area
        self.hand = []
        self.play_area = []
        
    def display_all(self,board_state):
        print(self.name,'\'s hand is:',sep='')
        print([card for card in self.hand])
        #print(self.name,'deck is:',[card for card in self.deck])
        #print(self.name,'discard pile is:',[card for card in self.discard_pile])
        #print(self.name,'play area is:',[card for card in self.play_area])
        print('Available:',self.actions_remaining,'actions,',self.buys_remaining,'buys,',self.count_coins(),'coins')
        print('Cards for purchase: ',board_state.display_supply())
        
    def reset_resources(self):
        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coins_elsewhere = 0
        self.coins_spent = 0
                    
    def take_turn(self,board_state,game): 
        print(self.name,'\'s turn begins',sep='')
        self.reset_resources()
        self.display_all(board_state)
        board_state.current_phase = 'Action'
        while board_state.current_phase == 'Action':
            board_state = self.action(board_state,game)
        while board_state.current_phase == 'Buy':
            board_state = self.buy(board_state,game)
        while board_state.current_phase == 'Cleanup':
            self.discard()
            self.draw(5)
            board_state.current_phase = 'Beginning'
        board_state.turn_counter += 1
        return 'Turn over'
            
    def action(self,board_state,game):
        if sum('Action' in card.type for card in self.hand) == 0:
            print('No actions in hand, buy phase begins')
            board_state.current_phase = 'Buy'
            return board_state
        if self.actions_remaining <= 0:
            print('No actions for turn remaining, buy phase begins')
            board_state.current_phase = 'Buy'
            return board_state
        print('Actions in hand:',[card.name for card in self.hand if 'Action' in card.type])
        command = game.input_handler(str(self.name+', enter action to play it, or enter Skip: '),[card.name.lower() for card in self.hand if 'Action' in card.type]+['skip'])
        if command == 'skip':
            board_state.current_phase = 'Buy'
            return board_state
        for i in range(len(self.hand)):
            if self.hand[i].name.lower() == command:
                self.play_area.append(self.hand.pop(i))
                board_state, game = game.card_dict[command].resolve(self, board_state, game)
                break        
        self.display_all(board_state)
        return board_state
    
    def buy(self,board_state,game):
        command = game.input_handler(str(self.name+', enter a card to buy, or enter Skip: '),[card for card in game.card_dict.keys()]+['skip'])
        if command == 'skip':
            board_state.current_phase = 'Cleanup'
            return board_state
        target = game.card_dict.get(command)
        if board_state.supply.get(target.name,0) <= 0:
            print("No more", target.name, "cards available")
            return board_state
        elif self.count_coins() < target.cost:
            print("Not enough money to buy a", target.name)
            return board_state
        else: 
            self.discard_pile.append(target)
            self.coins_spent += target.cost
            self.buys_remaining -= 1
            board_state.supply[target.name] -= 1
            print(self.name, "bought a",target.name)
            if self.buys_remaining <= 0:
                board_state.current_phase = 'Cleanup'
                print('No buys remaining, cleanup phase begins')
                return board_state
            self.display_all(board_state)
            return board_state
        
    def count_coins(self):
        return sum(card.coin_value for card in self.hand) + self.coins_elsewhere - self.coins_spent
    
    def trigger_reactions(self,attacking_player,attack,game):
        reactions = [card for card in self.hand if 'Reaction' in card.type]
        results = []
        for reaction in reactions:
            results.append(reaction.trigger(self,attacking_player,attack,game))
        return sum(results) >= 1
        
class Board_state:
    def __init__(self,supply,current_phase):
        self.supply = supply
        self.trash_pile = []
        self.turn_counter = 0
        self.current_phase = current_phase
    def display_supply(self):
        return self.supply

master_card_dict = {'gold':Gold(),'silver':Silver(),'copper':Copper(),'estate':Estate(),'duchy':Duchy(),'province':Province(),
             'smithy':Smithy(),'village':Village(),'cellar':Cellar(),'moat':Moat(),'moneylender':Moneylender(),'council room':Council_Room(),'throne room':Throne_Room(),'curse':Curse(),'witch':Witch(),'chapel':Chapel(),'vassal':Vassal(),'market':Market()}

#myplayer.hand.append(Smithy())
#myplayer.hand.append(Village())
#myplayer.hand.append(Cellar())
myboardstate = Board_state({'Smithy':10,'Copper':100,'Silver':100,'Gold':100,'Village':10,'Province':8,'Duchy':8,'Estate':8,'Cellar':10,'Moneylender':10,'Council Room':10,'Curse':20,'Witch':10,'Chapel':10,'Moat':10,'Vassal':10,'Throne Room':10,'Market':10},'Beginning')
mysavefolder = Save_Folder()
newergame = Game('A game',master_card_dict,myboardstate,[],mysavefolder)
newergame.new_game()



    

