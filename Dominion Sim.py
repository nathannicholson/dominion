# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 13:08:56 2020

@author: NNicholson
"""
import random
import shelve

class Game:
    def __init__(self,game_name,card_dict,supply,trash_pile,players):
        self.game_name = game_name
        self.card_dict = card_dict
        self.supply = supply
        self.players = players
        self.trash_pile = trash_pile
        self.turn_phase = 'Beginning'
        self.running = True
        
    def input_handler(self,prompt,allowables):
        allowables += ['help']
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
        print('Welcome to Dominion! Enter help at any time to get card text.')
        if self.players == []:
            self.choose_players([])
        if self.supply == {}: 
            self.choose_kingdoms(len(self.players))
        self.play_game()
        
    def choose_players(self,player_names):
        if self.players == []:
            command = ''
            while command.lower() != 'stop':
                command = input('Enter a player name, or enter stop to finish entering players: ')
                if command.lower() == 'stop':
                    if len(player_names) > 0:
                        break
                    else:
                        print('Must enter at least one player')
                        return self.choose_players(player_names)
                if command == '':
                    print('Must enter a name (can be anything)')
                    return self.choose_players(player_names)
                else:
                    player_names.append(command)
            self.players = [Player(name,[],[],[]) for name in player_names]
    
    def choose_kingdoms(self,number_of_players):
        number_of_players = min(4,number_of_players)
        curse_quantity = {1:10,2:10,3:20,4:30}
        victory_quantity = {1:8,2:8,3:12,4:12}
        money_quantity = {1:50,2:100,3:100,4:100}
        self.supply = {'Copper':money_quantity[number_of_players],'Silver':money_quantity[number_of_players],'Gold':money_quantity[number_of_players],'Estate':victory_quantity[number_of_players],
                           'Duchy':victory_quantity[number_of_players],'Province':victory_quantity[number_of_players],'Curse':curse_quantity[number_of_players]}
        command = self.input_handler('Enter random to choose 10 random kingdom cards for the supply, or enter custom to choose your own: ',['random','custom'])
        if command == 'random':
            kingdoms_chosen = sorted(random.sample([card for card in self.card_dict.values() if card.is_kingdom],10),key = lambda card: card.cost)
            for card in kingdoms_chosen:
                if 'Victory' in card.type:
                    self.supply[card.name] = victory_quantity[number_of_players]
                else:
                    self.supply[card.name] = 10
            print('10 random kingdom cards chosen:',', '.join([card.name for card in kingdoms_chosen]))
        elif command == 'custom':
            print('Available kingdom cards:',', '.join([card.name for card in self.card_dict.values()]))
            kingdom_count = 0
            while kingdom_count < 10:
                target = self.card_dict[self.input_handler(str('Enter a card to add to the supply. '+str(10 - kingdom_count)+' choices remaining: '),[key for key in self.card_dict if key in self.card_dict and self.card_dict[key].is_kingdom])]
                if 'Victory' in target.type:
                    self.supply[target.name] = victory_quantity[number_of_players]
                else:
                    self.supply[target.name] = 10
                kingdom_count += 1
            print('Finished choosing kingdoms, starting game')
            
    def display_supply(self):
        return self.supply
                
    def play_game(self,from_save = False):
        print(str('Game begins! \nPlayers: '+', '.join([player.name for player in self.players])+'\nEnter Help at any time to get card text.'))
        if from_save == False:
            for player in self.players:
                player.set_starting_deck()
                player.draw(5)
        while self.running:
            self.save_game()
            if self.input_handler('Continue? Enter Y to keep playing or N to quit: ',['y','n'])=='n':
                    self.running = False
                    print('Game ended')
                    break
            for player in self.players:
                print(player.take_turn(self))
                if self.game_over():
                    self.running = False
                    self.end()
                    break

    def save_game(self):
        save_file = shelve.open(self.game_name)
        save_file['Name'] = self.game_name
        save_file['Card Dict'] = self.card_dict
        save_file['Players'] = self.players
        save_file['Supply'] = self.supply
        save_file['Trash'] = self.trash_pile
        print('Game saved as \'',self.game_name,'\'',sep='')
                
    def game_over(self):
        return sum(1 for x in self.supply.values() if x <= 0) >= 3 or self.supply['Province'] <= 0
    
    def end(self):
        for player in self.players:
            player.victory_points = sum(card.victory_value for card in player.hand) + sum(card.victory_value for card in player.deck) + sum(card.victory_value for card in player.discard_pile) + sum(card.victory_value for card in player.play_area)
        self.winner_list = sorted([player for player in self.players],key = lambda player:player.victory_points,reverse = True)
        print('\nGame ends!',self.winner_list[0].name,'wins with',str(self.winner_list[0].victory_points),'victory points. \n\nRunners-up:\n')
        for player in self.winner_list[1:]:
            print(player.name,': ',str(player.victory_points),' victory points',sep='')

class Player:
    def __init__(self,name, hand, discard_pile, deck):
        self.victory_points = 0
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
                print('No cards left,',self.name,'drew their deck!')
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
        
    def display_all(self,game):
        print(self.name,'\'s hand is:',sep='')
        print([card for card in self.hand])
        #print(self.name,'deck is:',[card for card in self.deck])
        #print(self.name,'discard pile is:',[card for card in self.discard_pile])
        #print(self.name,'play area is:',[card for card in self.play_area])
        print('Available:',self.actions_remaining,'actions,',self.buys_remaining,'buys,',self.count_coins(),'coins')
        print('Cards for purchase: ',game.display_supply())
        
    def reset_resources(self):
        self.actions_remaining = 1
        self.buys_remaining = 1
        self.coins_elsewhere = 0
        self.coins_spent = 0
        
    def count_coins(self):
        return sum(card.coin_value for card in self.hand) + self.coins_elsewhere - self.coins_spent
    
    def trigger_reactions(self,attacking_player,attack,game):
        reactions = [card for card in self.hand if 'Reaction' in card.type]
        results = []
        for reaction in reactions:
            results.append(reaction.trigger(self,attacking_player,attack,game))
        return sum(results) >= 1
                    
    def take_turn(self,game): 
        print(self.name,'\'s turn begins',sep='')
        self.reset_resources()
        self.display_all(game)
        game.turn_phase = 'Action'
        while game.turn_phase == 'Action' and game.running:
            game = self.action(game)
        while game.turn_phase == 'Buy' and game.running:
            game = self.buy(game)
        while game.turn_phase == 'Cleanup' and game.running:
            self.discard()
            self.draw(5)
            game.turn_phase = 'Beginning'
        return 'Turn over'
            
    def action(self,game):
        if sum('Action' in card.type for card in self.hand) == 0:
            print('No actions in hand, buy phase begins')
            game.turn_phase = 'Buy'
            return game
        if self.actions_remaining <= 0:
            print('No actions for turn remaining, buy phase begins')
            game.turn_phase = 'Buy'
            return game
        print('Actions in hand:',[card.name for card in self.hand if 'Action' in card.type])
        command = game.input_handler(str(self.name+', enter action to play it, or enter Skip: '),[card.name.lower() for card in self.hand if 'Action' in card.type]+['skip'])
        if command == 'skip':
            game.turn_phase = 'Buy'
            return game
        for i in range(len(self.hand)):
            if self.hand[i].name.lower() == command:
                self.play_area.append(self.hand.pop(i))
                game = game.card_dict[command].resolve(self, game)
                break        
        self.display_all(game)
        return game
    
    def buy(self,game):
        command = game.input_handler(str(self.name+', enter a card to buy, or enter Skip: '),[card for card in game.card_dict.keys()]+['skip'])
        if command == 'skip':
            game.turn_phase = 'Cleanup'
            return game
        target = game.card_dict.get(command)
        if game.supply.get(target.name,0) <= 0:
            print("No more", target.name, "cards available")
            return game
        elif self.count_coins() < target.cost:
            print("Not enough money to buy a", target.name)
            return game
        else: 
            self.discard_pile.append(target)
            self.coins_spent += target.cost
            self.buys_remaining -= 1
            game.supply[target.name] -= 1
            print(self.name, "bought a",target.name)
            if self.buys_remaining <= 0:
                game.turn_phase = 'Cleanup'
                print('No buys remaining, cleanup phase begins')
                return game
            self.display_all(game)
            return game

class Card:
    def __init__(self):
        self.victory_value = 0
        self.coin_value = 0
        self.cost = 0
        self.name = ''
        self.type = []
        self.is_kingdom = True
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
        self.is_kingdom = False
        self.description = 'Treasure worth 1 coin'
        
class Curse(Card):
    def __init__(self):
        Card.__init__(self)
        self.name = 'Curse'
        self.type = ['Curse']
        self.is_kingdom = False
        self.victory_value = -1
        self.description = 'Junk worth -1 victory points'

class Silver(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.coin_value = 2
        self.name = 'Silver'
        self.type = ['Treasure']
        self.is_kingdom = False
        self.description = 'Treasure worth 2 coins'
        
class Gold(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 6
        self.coin_value = 3
        self.name = 'Gold'
        self.type = ['Treasure']
        self.is_kingdom = False
        self.description = 'Treasure worth 3 coins'
        
class Estate(Card):
    def __init__(self):
        Card.__init__(self)
        self.victory_value = 1
        self.name = 'Estate'
        self.type = ['Victory']
        self.is_kingdom = False
        self.description = 'Victory card worth 1 victory point'
 
        
class Duchy(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.victory_value = 3
        self.name = 'Duchy'
        self.type = ['Victory']
        self.is_kingdom = False
        self.description = 'Victory card worth 5 victory points'
        
class Province(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 8
        self.victory_value = 6
        self.name = 'Province'
        self.type = ['Victory']
        self.is_kingdom = False
        self.description = 'Victory card worth 8 victory points'

class Cellar(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 2
        self.name = 'Cellar'
        self.type = ['Action']
        self.description = '+1 Action. Discard any number of cards, then draw that many cards.'
        
    def resolve(self,player,game):
        print(player.name,'plays a',self.name)
        cards_discarded = 0
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
                        cards_discarded +=1
                        break
            else:
                print('No more cards in hand to discard')
                break
        player.draw(cards_discarded)
        return game
    
class Chapel(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 2
        self.name = 'Chapel'
        self.type = ['Action']
        self.description = 'Trash up to 4 cards from your hand.'
        self.cards_trashed = 0
        
    def resolve(self,player,game):
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
                        game.trash_pile.append(player.hand.pop(i))
                        self.cards_trashed += 1
                        break
            else:
                print('No more cards in hand to trash')
                break
        print(player.name,'finished resolving',self.name)
        player.actions_remaining -= 1
        return game
    
class CouncilRoom(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.name = 'Council Room'
        self.type =['Action']
        self.description = '+4 cards, +1 buy. Each other play draws a card.'
    
    def resolve(self,player,game):
        print(player.name,'plays a',self.name)
        player.draw(4)
        player.buys_remaining += 1
        for person in game.players:
            if person.name != player.name:
                person.draw(1)
        player.actions_remaining -= 1
        return game

class Harbinger(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Harbinger'
        self.type = ['Action']
        self.description = '+1 Card, +1 Action. Look through your discard pile. You may put a card from it on top of your deck.'
        
    def resolve(self,player,game):
        print(player.name,'plays a',self.name)
        command = ''
        while command != 'skip':
            print(player.name,'\'s discard pile is:',[card for card in player.discard_pile])
            command = game.input_handler(str(player.name+', enter a card to put on top of your deck, or enter skip: '),[key for key in game.card_dict]+['skip'])
            if command == 'skip':
                continue
            if sum(card.name.lower() == command for card in player.discard_pile) == 0:
                print('No such card in discard pile, try again')
                continue
            if len(player.discard_pile) > 0:
                for i in range(len(player.discard_pile)):
                    if player.discard_pile[i].name.lower() == command:
                        print(player.name,'puts a',player.discard_pile[i].name,'on top of their deck.')
                        player.deck.insert(0,player.discard_pile.pop(i))
                        break
                break
            else:
                print('No cards in discard pile')
                break
        return game

class Market(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.name = 'Market'
        self.type = ['Action']
        self.description = '+1 card, +1 action, +1 buy, +1 coin.'
    
    def resolve(self,player, game):
        print(player.name,'plays a',self.name)
        player.draw(1)
        player.buys_remaining += 1
        player.coins_elsewhere += 1
        return game

class Moat(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 2
        self.name = 'Moat'
        self.type = ['Action','Reaction']
        self.description = '+2 cards. Whenever another player plays an attack card, you may reveal this to be unaffected by the attack.'

    def trigger(self,owning_player,attacking_player,attack,game):
        print('Hey ',owning_player.name,', ',attacking_player.name,' is playing a ',attack.name,'!. Reveal Moat to nullify the attack against you?',sep = '')
        command = game.input_handler('Enter Y or N: ',['y','n'])
        if command == 'y':
            print(owning_player.name,'reveals a',self.name,'and is unaffected by',attack.name,'.')
            return True
        else:
            print(owning_player.name,'declines to reveal',self.name)
            return False
        
    def resolve(self,player, game):
        print(player.name,'plays a',self.name)
        player.draw(2)
        player.actions_remaining -= 1
        return game
        
class Moneylender(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 4
        self.name = 'Moneylender'
        self.type = ['Action']
        self.description = 'You may trash a Copper from your hand for 3 coins.'
        
    def resolve(self,player, game):
        print(player.name,'plays a',self.name)
        if sum(card.name == 'Copper' for card in player.hand) > 0:
            command = game.input_handler('Trash a Copper for 3 coins? Enter Y or N: ',['y','n'])
            if command == 'y':
                player.coins_elsewhere += 3
                print(player.name, 'trashed a Copper for 3 coins.')
                for i in range(len(player.hand)):
                    if player.hand[i].name == 'Copper':
                        game.trash_pile.append(player.hand.pop(i))
                        break
        else:
            print('No coppers in hand, nothing to trash')                
        player.actions_remaining -= 1
        return game

class Smithy(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 4
        self.name = 'Smithy'
        self.type = ['Action']
        self.description = '+3 cards.'
        
    def resolve(self,player, game):
        print(player.name,'plays a',self.name)
        player.draw(3)
        player.actions_remaining -= 1
        return game
    
class ThroneRoom(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 4
        self.name = 'Throne Room'
        self.type = ['Action']
        self.description = 'You may play an action card from your hand twice.'
        
    def resolve(self,player, game):
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
                            game = game.card_dict[command].resolve(player, game)
                            game = game.card_dict[command].resolve(player, game)
                            break
                    break
            else:
                print('No actions in hand, nothing to',self.name)
                break
        return game

class Vassal(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Vassal'
        self.type = ['Action']
        self.description = '+2 coins. Discard the top card of your deck. If it\'s an action card, you may play it.'
        
    def resolve(self,player,game):
        print(player.name,' plays a',self.name)
        if len(player.deck) < 1:
            print('No cards remaining in deck, so nothing discarded to',self.name)
        else:
            target = player.deck[0]
            print(player.name,'discards a',target.name)
            if 'Action' in target.type:
                command = game.input_handler(str('Play the discarded '+target.name+'? Enter Y or N: '),['y','n'])
                if command == 'y':
                    player.play_area.append(player.deck.pop(0))
                    game = target.resolve(player, game)
                else:
                    player.discard_pile.append(player.deck.pop(0))
            else:
                player.discard_pile.append(player.deck.pop(0))
            
        player.coins_elsewhere += 2
        player.actions_remaining -= 1
        return game
    
class Village(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Village'
        self.type = ['Action']
        self.description = '+1 card, +2 actions.'
        
    def resolve(self,player,game):
        print(player.name,' plays a',self.name)
        player.draw(1)
        player.actions_remaining += 1
        return game

class Witch(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 5
        self.name = 'Witch'
        self.type = ['Action']
        self.description = '+2 cards. Each other player gains a Curse.'
        
    def resolve(self,player,game):
        immunity = False
        print(player.name,'plays a',self.name)
        player.draw(2)
        player.actions_remaining -= 1
        for victim in game.players:
            if victim.name != player.name:
                immunity = victim.trigger_reactions(player,self,game)
                if immunity == False:
                    if game.supply['Curse'] > 0:
                        victim.discard_pile.append(Curse())
                        game.supply['Curse'] -= 1
                        print(victim.name,'gains a Curse')
                    else:
                        print('No curses remain,',victim.name,'is unaffected by Witch')
            immunity = False
        return game

class Workshop(Card):
    def __init__(self):
        Card.__init__(self)
        self.cost = 3
        self.name = 'Workshop'
        self.type = ['Action']   
        self.description = 'Gain a card costing up to 4.'
        
    def resolve(self,player,game):
        print(player.name,'plays a',self.name)
        command = game.input_handler('Enter a card to gain, costing up to 4: ',[card.lower() for card in game.supply.keys() if game.supply.get(card,0) > 0])
        while game.card_dict.get(command,0).cost > 4:
            command = game.input_handler('Too expensive, enter another card: ',[card.lower() for card in game.supply.keys() if game.supply.get(card,0) > 0])
        target = game.card_dict.get(command)
        player.discard_pile.append(game.card_dict[target.name.lower()])
        game.supply[target.name] -= 1
        print(player.name,'gained a ',target.name)
        player.actions_remaining -= 1
        return game
        
def load_game(filename):
    save_file = shelve.open(filename)
    loaded_game = Game(save_file['Name'],save_file['Card Dict'],save_file['Supply'],save_file['Trash'],save_file['Players'])
    loaded_game.play_game(True)

master_card_dict = {'gold':Gold(),'silver':Silver(),'copper':Copper(),'estate':Estate(),'duchy':Duchy(),'province':Province(),
             'smithy':Smithy(),'village':Village(),'cellar':Cellar(),'moat':Moat(),'harbinger':Harbinger(),'moneylender':Moneylender(),'council room':CouncilRoom(),'throne room':ThroneRoom(),'curse':Curse(),'witch':Witch(),'chapel':Chapel(),'vassal':Vassal(),'market':Market(),'workshop':Workshop()}

mygame = Game('My game',master_card_dict,{},[],[])  

mygame.new_game()



    

