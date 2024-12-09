from dataclasses import dataclass
from typing import Dict, List, Optional
import random
from collections import deque
from copy import deepcopy
import re
from collections import defaultdict
from agents.llama_agent import Llama3_Agent
from agents.llama2_agent import Llama2_Agent
from agents.qwen_agent import Qwen_Agent
from agents.phi3_agent import Phi3_Agent
from agents.gemma_agent import GEMMA_Agent
from agents.mistral_agent import Mistral_Agent
from agents.ensemble_agent import Ensemble_Agent
import json
import os
import logging
import time
from PIL import Image, ImageDraw, ImageFont
import math

@dataclass
class Property:
    name: str
    price: int
    rent: List[int]
    house_price: int
    color_set: str
    number_in_set: int
    mortgage_value: int
    mortgage_fee: int
    coordinates: List[tuple[int, int]] = None
    is_mortgaged: bool = False
    number_of_houses: int = 0
    number_of_hotels: int = 0
    owned_by: Optional[int] = None

@dataclass
class Railroad:
    name: str
    price: int
    rent: List[int]
    mortgage_value: int
    mortgage_fee: int
    coordinates: List[tuple[int, int]] = None
    is_mortgaged: bool = False
    owned_by: Optional[int] = None

@dataclass
class Utility:
    name: str
    price: int
    mortgage_value: int
    mortgage_fee: int
    coordinates: List[tuple[int, int]] = None
    is_mortgaged: bool = False
    owned_by: Optional[int] = None

@dataclass
class Tax:
    name: str
    type: str
    amount: int
    coordinates: List[tuple[int, int]] = None

@dataclass
class SpecialSpace:
    name: str
    coordinates: List[tuple[int, int]] = None

PurchaseableProperty = Property | Railroad | Utility

MONOPOLY_BOARD = [
    SpecialSpace("Go", [(1729, 1729), (2000, 2000)]),
    Property("Mediterranean Avenue", 60, [2, 10, 30, 90, 160, 250], 50, "brown", 2, 30, 33, [(1562, 1729), (1729, 2000)], False, 0, 0, None),
    SpecialSpace("Community Chest", [(1409, 1729), (1562, 2000)]),
    Property("Baltic Avenue", 60, [4, 20, 60, 180, 320, 450], 50, "brown", 2, 30, 33, [(1249, 1729), (1409, 2000)], False, 0, 0, None),
    Tax("Income Tax", "tax", 200, [(1086, 1729), (1249, 2000)]),
    Railroad("Reading Railroad", 200, [25, 50, 100, 200], 100, 110, [(923, 1729), (1086, 2000)], False, None),
    Property("Oriental Avenue", 100, [6, 30, 90, 270, 400, 550], 50, "light_blue", 3, 50, 55, [(760, 1729), (923, 2000)], False, 0, 0, None),
    SpecialSpace("Chance", [(597, 1729), (760, 2000)]),
    Property("Vermont Avenue", 100, [6, 30, 90, 270, 400, 550], 50, "light_blue", 3, 50, 55, [(434, 1729), (597, 2000)], False, 0, 0, None),
    Property("Connecticut Avenue", 120, [8, 40, 100, 300, 450, 600], 50, "light_blue", 3, 60, 66, [(271, 1729), (434, 2000)], False, 0, 0, None),
    SpecialSpace("Jail/Just Visiting", [(0, 1729), (271, 2000)]),
    Property("St. Charles Place", 140, [10, 50, 150, 450, 625, 750], 100, "pink", 3, 70, 77, [(0, 1562), (271, 1729)], False, 0, 0, None),
    Utility("Electric Company", 150, 75, 83, [(0, 1400), (271, 1562)], False, None),
    Property("States Avenue", 140, [10, 50, 150, 450, 625, 750], 100, "pink", 3, 70, 77, [(0, 1249), (271, 1400)], False, 0, 0, None),
    Property("Virginia Avenue", 160, [12, 60, 180, 500, 700, 900], 100, "pink", 3, 80, 88, [(0, 1086), (271, 1249)], False, 0, 0, None),
    Railroad("Pennsylvania Railroad", 200, [25, 50, 100, 200], 100, 110, [(0, 923), (271, 1086)], False, None),
    Property("St. James Place", 180, [14, 70, 200, 550, 750, 950], 100, "orange", 3, 90, 99, [(0, 760), (271, 923)], False, 0, 0, None),
    SpecialSpace("Community Chest", [(0, 597), (271, 760)]),
    Property("Tennessee Avenue", 180, [14, 70, 200, 550, 750, 950], 100, "orange", 3, 90, 99, [(0, 434), (271, 597)], False, 0, 0, None),
    Property("New York Avenue", 200, [16, 80, 220, 600, 800, 1000], 100, "orange", 3, 100, 110, [(0, 271), (271, 434)], False, 0, 0, None),
    SpecialSpace("Free Parking", [(0, 0), (271, 271)]),
    Property("Kentucky Avenue", 220, [18, 90, 250, 700, 875, 1050], 150, "red", 3, 110, 121, [(271, 0), (434, 271)], False, 0, 0, None),
    SpecialSpace("Chance", [(434, 0), (597, 271)]),
    Property("Indiana Avenue", 220, [18, 90, 250, 700, 875, 1050], 150, "red", 3, 110, 121, [(597, 0), (760, 271)], False, 0, 0, None),
    Property("Illinois Avenue", 240, [20, 100, 300, 750, 925, 1100], 150, "red", 3, 120, 132, [(760, 0), (923, 271)], False, 0, 0, None),
    Railroad("B. & O. Railroad", 200, [25, 50, 100, 200], 100, 110, [(923, 0), (1086, 271)], False, None),
    Property("Atlantic Avenue", 260, [22, 110, 330, 800, 975, 1150], 150, "yellow", 3, 130, 143, [(1086, 0), (1249, 271)], False, 0, 0, None),
    Property("Ventnor Avenue", 260, [22, 110, 330, 800, 975, 1150], 150, "yellow", 3, 130, 143, [(1249, 0), (1409, 271)], False, 0, 0, None),
    Utility("Water Works", 150, 75, 83, [(1409, 0), (1573, 271)], False, None),
    Property("Marvin Gardens", 280, [24, 120, 360, 850, 1025, 1200], 150, "yellow", 3, 140, 154, [(1573, 0), (1729, 271)], False, 0, 0, None),
    SpecialSpace("Go To Jail", [(1729, 0), (2000, 271)]),
    Property("Pacific Avenue", 300, [26, 130, 390, 900, 1100, 1275], 200, "green", 3, 150, 165, [(1729, 271), (2000, 434)], False, 0, 0, None),
    Property("North Carolina Avenue", 300, [26, 130, 390, 900, 1100, 1275], 200, "green", 3, 150, 165, [(1729, 434), (2000, 597)], False, 0, 0, None),
    SpecialSpace("Community Chest", [(1729, 597), (2000, 760)]),
    Property("Pennsylvania Avenue", 320, [28, 150, 450, 1000, 1200, 1400], 200, "green", 3, 160, 176, [(1729, 760), (2000, 923)], False, 0, 0, None),
    Railroad("Short Line", 200, [25, 50, 100, 200], 100, 110, [(1729, 923), (2000, 1086)], False, None),
    SpecialSpace("Chance", [(1729, 1086), (2000, 1249)]),
    Property("Park Place", 350, [35, 175, 500, 1100, 1300, 1500], 200, "dark_blue", 2, 175, 193, [(1729, 1249), (2000, 1400)], False, 0, 0, None),
    Tax("Luxury Tax", "tax", 100, [(1729, 1400), (2000, 1562)]),
    Property("Boardwalk", 400, [50, 200, 600, 1400, 1700, 2000], 200, "dark_blue", 2, 200, 220, [(1729, 1562), (2000, 1729)], False, 0, 0, None),
]


class MonopolyGame:
    def __init__(self, num_players: int, llm_player_id: int, llm = 'manual'):
        self.num_players = num_players
        self.game_ended = False
        self.board = self._initialize_board()
        self.players = self._initialize_players()
        self.llm_player_id = llm_player_id
        self.current_player = 0
        self.num_rounds = 0
        self.actions_taken = 0
        self.last_dice_roll = (0, 0)
        self.chance_cards = self._initialize_cards()
        self.community_chest_cards = self._initialize_cards()
        self.remaining_houses = 32
        self.remaining_hotels = 12
        self.llm = llm
        self.agent = self._initialize_llm(llm)
        self.llm_memory = deque(maxlen=3)
        self.stats = {
            player["id"]: {
                "properties_bought": 0,
                "mortgages": 0,
                "unmortgages": 0,
                "houses_built": 0,
                "houses_sold": 0,
                "rent_paid": 0,
                "rent_received": 0,
                "actions_taken": 0,
            } for player in self.players
        }
        self.stats[self.llm_player_id]["invalid_json"] = 0
        self.stats[self.llm_player_id]["invalid_move"] = 0
        self.stats[self.llm_player_id]["defaulted_move"] = 0

    def _initialize_players(self):
        players = [
            {
                "id": i,
                "position": 0,
                "money": 1500,
                "properties": [],
                "in_jail": False,
                "turns_in_jail": 0,
                "get_out_of_jail_cards": 0
            } for i in range(self.num_players)
        ]
        return players

    def _initialize_board(self):
        return deepcopy(MONOPOLY_BOARD)

    def _initialize_cards(self):
        return deque(random.sample(range(16), 16))
    
    def _initialize_llm(self, llm):
        if llm == "llama2":
            return Llama2_Agent()
        elif llm == "llama3":
            return Llama3_Agent()
        elif llm == "qwen":
            return Qwen_Agent()
        elif llm == "phi3":
            return Phi3_Agent()
        elif llm == "gemma2":
            return GEMMA_Agent()
        elif llm == "mistral":
            return Mistral_Agent()            
        elif llm == "ensemble":
            return Ensemble_Agent()
        return None
    
    def get_net_worth(self, player_id: int):
        player = self.players[player_id]
        net_worth = player["money"]

        for property in player["properties"]:
            if not property.is_mortgaged:
                net_worth += property.price
                if isinstance(property, Property):
                    net_worth += (property.number_of_hotels + property.number_of_houses) * property.house_price
            else:
                net_worth += property.price - property.mortgage_fee
        
        return net_worth

    def get_sell_worth(self, player_id: int):
        player = self.players[player_id]
        sell_worth = 0

        for property in player["properties"]:
            if not property.is_mortgaged:
                sell_worth += property.mortgage_value
                if isinstance(property, Property):
                    sell_worth += (property.number_of_hotels + property.number_of_houses) * (property.house_price // 2)
        
        return sell_worth
    
    def roll_dice(self):
        dice_1 = 3
        dice_2 = 3
        double_rolled = True if dice_1 == dice_2 else False
        self.last_dice_roll = (dice_1, dice_2)

        return (dice_1, dice_2, double_rolled)
    
    def move_player(self, player_id: int, dice_1=None, dice_2=None, new_position=None, go_back_3_spaces=False):
        current_position = self.players[player_id]["position"]
        if new_position is None and dice_1 and dice_2:
            new_position = self.players[player_id]["position"] + dice_1 + dice_2

        new_position = new_position % len(self.board)
        self.players[player_id]["position"] = new_position
        space = self.board[new_position]

        if dice_1 or dice_2:
            print(f"Player {player_id} rolled {(dice_1, dice_2)} and landed on {space.name}")
        else:
            print(f"Player {player_id} moved to {space.name}")
        
        if current_position > new_position and not go_back_3_spaces:
            self.pass_go(player_id)
        
        self.actions_taken += 1
        self.save_board_image(self.actions_taken)

    def pass_go(self, player_id: int):
        self.players[player_id]["money"] += 200

        print(f"Player {player_id} passed Go and got $200") 
    
    def go_to_jail(self, player_id: int):
        self.players[player_id]["in_jail"] = True
        self.players[player_id]["turns_in_jail"] = 1
        self.players[player_id]["position"] = 10

        print(f"Player {player_id} went to jail")
    
    def draw_chance(self, player_id: int):
        if len(self.chance_cards) == 0:
            self.chance_cards = self._initialize_cards()
        card = self.chance_cards.popleft()
        position = self.players[player_id]["position"]
        multiplier = False

        match card:
            case 0:
                print(f"Player {player_id} drew: Advance to Boardwalk.")
                self.move_player(player_id, new_position=39)
            case 1:
                print(f"Player {player_id} drew: Advance to Go (Collect $200).")
                self.move_player(player_id, new_position=0)
            case 2:
                print(f"Player {player_id} drew: Advance to Illinois Avenue. If you pass Go, collect $200.")
                self.move_player(player_id, new_position=24)
            case 3:
                print(f"Player {player_id} drew: Advance to St. Charles Place. If you pass Go, collect $200.")
                self.move_player(player_id, new_position=11)
            case x if 4 <= x <= 5:
                print(f"Player {player_id} drew: Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled.")
                if position > 35 or position <= 5:
                    self.move_player(player_id, new_position=5)
                elif position <= 15:
                    self.move_player(player_id, new_position=15)
                elif position <= 25:
                    self.move_player(player_id, new_position=25)
                else:
                    self.move_player(player_id, new_position=35)
                multiplier = True
            case 6:
                print(f"Player {player_id} drew: Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total ten times amount thrown.")
                if 12 < position <= 28:
                    self.move_player(player_id, new_position=28)
                else:
                    self.move_player(player_id, new_position=12)
                multiplier = True
            case 7:
                print(f"Player {player_id} drew: Bank pays you dividend of $50.")
                self.players[player_id]["money"] += 50
            case 8:
                print(f"Player {player_id} drew: Get Out of Jail Free.")
                self.players[player_id]["get_out_of_jail_cards"] += 1
            case 9:
                print(f"Player {player_id} drew: Go Back 3 Spaces.")
                self.move_player(player_id, new_position=position-3, go_back_3_spaces=True)
            case 10:
                print(f"Player {player_id} drew: Go to Jail. Go directly to Jail, do not pass Go, do not collect $200.")
                self.go_to_jail(player_id)
            case 11:
                print(f"Player {player_id} drew: Make general repairs on all your property. For each house pay $25. For each hotel pay $100.")
                properties = self.players[player_id]["properties"]
                total_houses = 0
                total_hotels = 0
                for property in properties:
                    if isinstance(property, Property):
                        total_houses += property.number_of_houses
                        total_hotels += property.number_of_hotels
                self.players[player_id]["money"] -= (total_houses * 25 + total_hotels * 100)
            case 12:
                print(f"Player {player_id} drew: Speeding fine $15.")
                self.players[player_id]["money"] -= 15
            case 13:
                print(f"Player {player_id} drew: Take a trip to Reading Railroad. If you pass Go, collect $200.")
                self.move_player(player_id, new_position=5)
            case 14:
                print(f"Player {player_id} drew: You have been elected Chairman of the Board. Pay each player $50.")
                self.players[player_id]["money"] -= len(self.players) * 50
                for player in self.players:
                    if player["id"] != player_id:
                        player["money"] += 50
            case 15:
                print(f"Player {player_id} drew: Your building loan matures. Collect $150")
                self.players[player_id]["money"] += 150
            case _:
                pass
        return multiplier
    
    def draw_community_chest(self, player_id: int):
        if len(self.community_chest_cards) == 0:
            self.community_chest_cards = self._initialize_cards()
        card = self.community_chest_cards.popleft()

        match card:
            case 0:
                print(f"Player {player_id} drew: Advance to Go (Collect $200)")
                self.move_player(player_id, new_position=0)
            case 1:
                print(f"Player {player_id} drew: Bank error in your favor. Collect $200")
                self.players[player_id]["money"] += 200
            case 2:
                print(f"Player {player_id} drew: Doctor’s fee. Pay $50")
                self.players[player_id]["money"] -= 50
            case 3:
                print(f"Player {player_id} drew: From sale of stock you get $50")
                self.players[player_id]["money"] += 50
            case 4:
                print(f"Player {player_id} drew: Get Out of Jail Free")
                self.players[player_id]["get_out_of_jail_cards"] += 1
            case 5:
                print(f"Player {player_id} drew: Go to Jail. Go directly to Jail, do not pass Go, do not collect $200")
                self.go_to_jail(player_id)
            case 6:
                print(f"Player {player_id} drew: Holiday fund matures. Receive $100")
                self.players[player_id]["money"] += 100
            case 7:
                print(f"Player {player_id} drew: Income tax refund. Collect $20")
                self.players[player_id]["money"] += 20
            case 8:
                print(f"Player {player_id} drew: It is your birthday. Collect $10 from every player")
                self.players[player_id]["money"] += len(self.players) * 10
                for player in self.players:
                    if player["id"] != player_id:
                        player["money"] -= 10
            case 9:
                print(f"Player {player_id} drew: Life insurance matures. Collect $100")
                self.players[player_id]["money"] += 100
            case 10:
                print(f"Player {player_id} drew: Pay hospital fees of $100")
                self.players[player_id]["money"] -= 100
            case 11:
                print(f"Player {player_id} drew: Pay school fees of $50")
                self.players[player_id]["money"] -= 50
            case 12:
                print(f"Player {player_id} drew: Receive $25 consultancy fee")
                self.players[player_id]["money"] += 25
            case 13:
                print(f"Player {player_id} drew: You are assessed for street repair. $40 per house. $115 per hotel")
                properties = self.players[player_id]["properties"]
                total_houses = 0
                total_hotels = 0
                for property in properties:
                    if isinstance(property, Property):
                        total_houses += property.number_of_houses
                        total_hotels += property.number_of_hotels
                self.players[player_id]["money"] -= (total_houses * 40 + total_hotels * 115)
            case 14:
                print(f"Player {player_id} drew: You have won second prize in a beauty contest. Collect $10")
                self.players[player_id]["money"] += 10
            case 15:
                print(f"Player {player_id} drew: You inherit $100")
                self.players[player_id]["money"] += 100
            case _:
                pass

    def get_current_player(self):
        return self.players[self.current_player]

    def next_turn(self):
        self.current_player = (self.current_player + 1) % self.num_players
        if self.current_player == 0:
            self.num_rounds += 1
            print(f"\nRound {self.num_rounds}")
    
    def purchase_property(self, player_id: int, property: PurchaseableProperty):
        self.players[player_id]["properties"].append(property)
        self.players[player_id]["money"] -= property.price
        property.owned_by = player_id
        self.stats[player_id]["properties_bought"] += 1

        print(f"Player {player_id} bought {property.name} for ${property.price}")
    
    def build_house(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
        self.stats[player_id]["houses_built"] += 1
        for property in properties:
            if property.name == property_name:
                if property.number_of_houses < 4:
                    self.remaining_houses -= 1
                    property.number_of_houses += 1
                    player["money"] -= property.house_price
                    print(f"Player {player_id} built a house on {property_name}")
                else:
                    self.remaining_houses += 4
                    self.remaining_hotels -= 1
                    property.number_of_houses = 0
                    property.number_of_hotels = 1
                    player["money"] -= property.house_price
                    print(f"Player {player_id} built a hotel on {property_name}")

    def sell_house(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
        self.stats[player_id]["houses_sold"] += 1
        for property in properties:
            if property.name == property_name:
                if property.number_of_hotels == 1:
                    self.remaining_houses -= 4
                    self.remaining_hotels += 1
                    property.number_of_houses = 4
                    property.number_of_hotels = 0
                    player["money"] += (property.house_price // 2)
                    print(f"Player {player_id} sold a hotel on {property_name}")
                else:
                    self.remaining_houses += 1
                    property.number_of_houses -= 1
                    player["money"] += (property.house_price // 2)
                    print(f"Player {player_id} sold a house on {property_name}")

    def get_jail_actions(self, player_id: int):
        player = self.players[player_id]
        available_actions = []

        if player["get_out_of_jail_cards"] > 0:
            available_actions.append("Use a Get Out of Jail Free card")
        if player["money"] >= 50:
            available_actions.append("Pay $50")
        available_actions.append("Roll for a double")
        return available_actions
    
    def select_jail_action(self, player_id: int, actions: List[str], selected_index: int):
        player = self.players[player_id]
        action = actions[selected_index]
        self.stats[player_id]["actions_taken"] += 1
        action_type = action.split(" ")[0]
        dice_1, dice_2, double_rolled = self.roll_dice()

        if action_type == "Use":
            player["turns_in_jail"] = 0
            player["in_jail"] = False
            player["get_out_of_jail_cards"] -= 1
            print(f"Player {player_id} used a Get Out of Jail Free card")
            return (dice_1, dice_2, double_rolled)
        elif action_type == "Pay":
            player["turns_in_jail"] = 0
            player["in_jail"] = False
            player["money"] -= 50
            print(f"Player {player_id} paid $50 to leave jail")
            return (dice_1, dice_2, double_rolled)
        else:
            if double_rolled:
                print(f"Player {player_id} rolled a double and got out of jail")
                return (dice_1, dice_2, False)
            else:
                if player["turns_in_jail"] == 3:
                    player["turns_in_jail"] = 0
                    player["in_jail"] = False
                    player["money"] -= 50
                    print(f"Player {player_id} did not roll a double and paid $50")
                    return (dice_1, dice_2, False)
                else:
                    player["turns_in_jail"] += 1
                    print(f"Player {player_id} rolled {(dice_1, dice_2)} and stayed in jail")
                    return (-1, -1, False)

    def mortgage_property(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
        self.stats[player_id]["mortgages"] += 1
        for property in properties:
            if property.name == property_name:
                property.is_mortgaged = True
                player["money"] += property.mortgage_value
                print(f"Player {player_id} mortgaged {property.name} for ${property.mortgage_value}")
                self.print_player_state(player_id)

    def unmortgage_property(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
        self.stats[player_id]["unmortgages"] += 1
        for property in properties:
            if property.name == property_name:
                property.is_mortgaged = False
                player["money"] -= property.mortgage_fee
                print(f"Player {player_id} unmortgaged {property.name} for ${property.mortgage_fee}")
    
    def pay_rent(self, player_1_id: int, player_2_id: int, property: PurchaseableProperty, dice_roll: int, multiplier: bool):
        player_2_properties = self.players[player_2_id]["properties"]
        if isinstance(property, Property):
            owned_color_set = 0
            for other_property in player_2_properties:
                if isinstance(other_property, Property) and other_property.color_set == property.color_set:
                    owned_color_set += 1

            rent_index = property.number_of_houses + property.number_of_hotels * 5
            if rent_index == 0 and owned_color_set == property.number_in_set:
                rent = property.rent[rent_index] * 2
            else:
                rent = property.rent[rent_index]
        elif isinstance(property, Railroad):
            owned_railroads = 0
            for other_property in player_2_properties:
                if isinstance(other_property, Railroad):
                    owned_railroads += 1
            rent = property.rent[owned_railroads - 1]
            if multiplier:
                rent *= 2
        elif isinstance(property, Utility):
            owned_utilities = 0
            for other_property in player_2_properties:
                if isinstance(other_property, Utility):
                    owned_utilities += 1
            if owned_utilities == 2 or multiplier:
                rent = 10 * dice_roll
            else:
                rent = 4 * dice_roll

        self.players[player_1_id]["money"] -= rent
        self.players[player_2_id]["money"] += rent     
        self.stats[player_1_id]["rent_paid"] += rent
        self.stats[player_2_id]["rent_received"] += rent
        print(f"Player {player_1_id} paid ${rent} in rent to player {player_2_id}")
    
    def baseline_strategy(self, player_id: int, space):
        player = self.players[player_id]
        if isinstance(space, PurchaseableProperty) and space.owned_by is None and space.price < player["money"]:
            self.actions_taken += 1
            self.stats[player_id]["actions_taken"] += 1
            self.purchase_property(player_id, space)
            self.save_board_image(self.actions_taken)
        
        actions = self.get_valid_actions(player_id, space)
        
        while any("Unmortgage" in action for action in actions):
            for index, action in enumerate(actions):
                if "Unmortgage" in action:
                    self.select_action(player_id, actions, index, space)
                    break
            actions = self.get_valid_actions(player_id, space)

        while any("Build" in action for action in actions):
            for index, action in enumerate(actions):
                if "Build" in action:
                    self.select_action(player_id, actions, index, space)
                    break
            actions = self.get_valid_actions(player_id, space)

        if player["in_jail"]:
            self.stats[player_id]["actions_taken"] += 1
            dice_1, dice_2, double_rolled = self.roll_dice()
            if player["get_out_of_jail_cards"] > 0:
                player["turns_in_jail"] = 0
                player["in_jail"] = False
                player["get_out_of_jail_cards"] -= 1
                print(f"Player {player_id} used a Get Out of Jail Free card")
            elif player["money"] >= 50:
                player["turns_in_jail"] = 0
                player["in_jail"] = False
                player["money"] -= 50
                print(f"Player {player_id} paid $50 to leave jail")
            else:
                if double_rolled:
                    print(f"Player {player_id} rolled a double and got out of jail")
                    double_rolled = False
                else:
                    if player["turns_in_jail"] == 3:
                        player["turns_in_jail"] = 0
                        player["in_jail"] = False
                        player["money"] -= 50
                        print(f"Player {player_id} did not roll a double and paid $50")
                        double_rolled = False
                    else:
                        print(f"Player {player_id} rolled {(dice_1, dice_2)} and stayed in jail")
                        player["turns_in_jail"] += 1
                        dice_1 = -1
                        dice_2 = -1
                        double_rolled = False

            return (dice_1, dice_2, double_rolled)
        return (-1, -1, False)
    
    def is_bankrupt(self, player_id: int):
        return (self.get_sell_worth(player_id) + self.players[player_id]["money"]) < 0
    
    def raise_money(self, player_id: int, space):
        player = self.players[player_id]

        if player_id == self.llm_player_id:
            self.request_action(player_id, space)
        else:
            while player["money"] < 0:
                actions = self.get_valid_actions(player_id, space)
                if any("Sell" in action for action in actions):
                    for index, action in enumerate(actions):
                        if "Sell" in action:
                            self.select_action(player_id, actions, index, space)
                            break
                elif any("Mortgage" in action for action in actions):
                    for index, action in enumerate(actions):
                        if "Mortgage" in action:
                            self.select_action(player_id, actions, index, space)
                            break
                    
            actions = self.get_valid_actions(player_id, space)

    def get_valid_actions(self, player_id: int, space):
        player = self.players[player_id]
        properties = player["properties"]
        available_actions = []

        if player["money"] >= 0:
            available_actions.append("End turn")

        if isinstance(space, PurchaseableProperty) and space.owned_by is None and space.price < player["money"]:
            available_actions.append(f"Purchase {space.name} for ${space.price}")
        
        color_sets = defaultdict(list)
        complete_color_sets = []
        for property in properties:
            if property.is_mortgaged:
                if player["money"] >= property.mortgage_fee:
                    available_actions.append(f"Unmortgage {property.name} for ${property.mortgage_fee}")
                continue
            if isinstance(property, Property):
                color_set = property.color_set
                color_sets[color_set].append(property)
                if len(color_sets[color_set]) == property.number_in_set:
                    complete_color_sets.append(color_set)
                if property.number_of_houses > 0 or property.number_of_hotels > 0:
                    continue
            available_actions.append(f"Mortgage {property.name} for ${property.mortgage_value}")
        
        for color_set in complete_color_sets:
            max_houses = max([property.number_of_houses + property.number_of_hotels * 5 for property in color_sets[color_set]])
            min_houses = min([property.number_of_houses + property.number_of_hotels * 5 for property in color_sets[color_set]])
            for property in color_sets[color_set]:
                num_houses = property.number_of_houses + property.number_of_hotels * 5
                if num_houses == min_houses:
                    if player["money"] >= property.house_price:
                        if num_houses < 4 and self.remaining_houses > 0:
                            available_actions.append(f"Build house on {property.name} for ${property.house_price}")
                        elif num_houses == 4 and self.remaining_hotels > 0:
                            available_actions.append(f"Build hotel on {property.name} for ${property.house_price}")
                if num_houses == max_houses:
                    if num_houses == 5 and self.remaining_houses >= 4:
                        available_actions.append(f"Sell hotel on {property.name} for ${property.house_price // 2}")
                    elif num_houses > 0:
                        available_actions.append(f"Sell house on {property.name} for ${property.house_price // 2}")
        
        return available_actions

    def select_action(self, player_id: int, actions: List[str], selected_index: int, space):
        action = actions[selected_index]
        action_type = action.split(" ")[0]
        self.actions_taken += 1
        self.stats[player_id]["actions_taken"] += 1

        if player_id == self.llm_player_id:
            prev_net_worth = self.get_net_worth(player_id)
            self.llm_memory.append({
                "action": action,
                "prev_net_worth": prev_net_worth,
                "new_net_worth": None,
            })

        if action_type == "Purchase":
            self.purchase_property(player_id, space)
        elif action_type == "Mortgage":
            pattern = r'^Mortgage ([A-Za-z]+(?:[.\s&]+[A-Za-z]+){0,4}) for \$(\d+(?:\.\d{2})?)$'
            match = re.match(pattern, action.strip())
            property_name = match.group(1)
            self.mortgage_property(player_id, property_name)
        elif action_type == "Unmortgage":
            pattern = r'^Unmortgage ([A-Za-z]+(?:[.\s&]+[A-Za-z]+){0,4}) for \$(\d+(?:\.\d{2})?)$'
            match = re.match(pattern, action.strip())
            property_name = match.group(1)
            self.unmortgage_property(player_id, property_name)
        elif action_type == "Build":
            pattern = r'^Build (house|hotel) on ([A-Za-z]+(?:[.\s&]+[A-Za-z]+){0,4}) for \$(\d+(?:\.\d{2})?)$'
            match = re.match(pattern, action.strip())
            property_name = match.group(2)
            self.build_house(player_id, property_name)
        elif action_type == "Sell":
            pattern = r'^Sell (house|hotel) on ([A-Za-z]+(?:[.\s&]+[A-Za-z]+){0,4}) for \$(\d+(?:\.\d{2})?)$'
            match = re.match(pattern, action.strip())
            property_name = match.group(2)
            self.sell_house(player_id, property_name)
        else:
            self.save_board_image(self.actions_taken)
            return
        
        self.save_board_image(self.actions_taken)

        if player_id == self.llm_player_id:
            self.llm_memory[-1]["new_net_worth"] = self.get_net_worth(player_id)

    def play_turn(self):
        player = self.get_current_player()
        player_id = player["id"]
        total_doubles = 0
        roll_again = True

        while roll_again:
            roll_again = False
            if self.players[player_id]["in_jail"]:
                if player_id == self.llm_player_id:
                    actions = self.get_jail_actions(player_id)
                    selected_index = -1
                    if self.agent:
                        attempts = 0
                        while selected_index == -1:
                            #default behavior if LLM keeps giving invalid moves
                            if attempts >= 5: 
                                #default to end turn or mortgage
                                selected_index = 0
                                self.stats[self.llm_player_id]["defaulted_move"] += 1
                            attempts += 1
                            selected_index = self.request_llm_action(actions)
                    else:
                        selected_index = self.request_user_action(actions)
                    dice_1, dice_2, double_rolled = self.select_jail_action(player_id, actions, selected_index)
                    if dice_1 == -1: #double roll to get out of jail failed, end turn
                        break
                else:
                    dice_1, dice_2, double_rolled = self.baseline_strategy(player_id, self.board[10])
                    if dice_1 == -1: #double roll to get out of jail failed, end turn
                        break
            else:
                dice_1, dice_2, double_rolled = self.roll_dice()

            if total_doubles >= 3:
                self.go_to_jail(player_id)
                break
            elif double_rolled > 0:
                roll_again = True
                total_doubles += 1
            self.move_player(player_id, dice_1, dice_2)

            new_position = player["position"]
            space = self.board[new_position]
            multiplier = False

            if space.name == "Go To Jail":
                self.go_to_jail(player_id)
            elif space.name == "Chance":
                multiplier = self.draw_chance(player_id)
            elif space.name == "Community Chest":
                self.draw_community_chest(player_id)
            elif "Tax" in space.name:
                player["money"] -= space.amount
                print(f"Player {player_id} paid ${space.amount} for {space.name}")
            
            if player["in_jail"]:
                break
            
            new_position = player["position"]
            space = self.board[new_position]

            if player["money"] < 0:
                if self.is_bankrupt(player_id):
                    self.game_ended = True
                    return
                self.raise_money(player_id, space)
                break

            if isinstance(space, PurchaseableProperty) and space.owned_by is not None and space.owned_by != player_id and not space.is_mortgaged:
                self.pay_rent(player_id, space.owned_by, space, (dice_1 + dice_2), multiplier)
                if player["money"] < 0:
                    if self.is_bankrupt(player_id):
                        self.game_ended = True
                        return
                    self.raise_money(player_id, space)
                    break

            if player_id == self.llm_player_id:
                self.request_action(player_id, space)
            else:
                self.baseline_strategy(player_id, space)
            
            self.print_player_state(player_id)

        self.next_turn()

    def play_game(self, max_rounds: int, game_num: int):
        print(f"\nGame {game_num} Start")
        start_time = time.time()
        while self.num_rounds < max_rounds and not self.game_ended:
            try:
                self.play_turn()
            except Exception as e:
                logging.error(e, exc_info=True)
        
        winner_id = max(range(len(self.players)), key=lambda i: self.get_net_worth(i))
        end_time = time.time()
        duration = end_time-start_time

        print(f"\nGame {game_num} Results")
        print(f"Game over after {self.num_rounds} round(s)")
        print(f"Game duration: {duration:.2f} seconds")
        print(f"Player {winner_id} won with a net worth of ${self.get_net_worth(winner_id)}")

        logging.info(f"\nGame {game_num} Results\n")
        logging.info(f"Game over after {self.num_rounds} round(s)\n")
        logging.info(f"Game duration: {duration:.2f} seconds\n")
        logging.info(f"Player {winner_id} ({'LLM' if winner_id == self.llm_player_id else 'Bot'}) won with a net worth of ${self.get_net_worth(winner_id)}\n")
        for player_id, player_stats in self.stats.items():
            logging.info(f"\nPlayer {player_id} ({'LLM' if player_id == self.llm_player_id else 'Bot'}) Stats:\n")
            for action, count in player_stats.items():
                logging.info(f"  {action.replace('_', ' ').capitalize()}: {count}\n")
        if self.llm == "ensemble":
            logging.info(f"Ensemble selection stats {dict(self.agent.selection_count)}")
        for player in self.players:
            logging.info(self.print_player_state(player["id"]) + "\n")
        
        return winner_id

    def request_action(self, player_id: int, space):
        selected_index = -1
        actions = self.get_valid_actions(player_id, space)

        while True:
            selected_index = -1
            if self.agent:
                attempts = 0
                while selected_index == -1:
                    #default behavior if LLM keeps giving invalid moves
                    if attempts >= 5: 
                        #default to end turn or mortgage
                        selected_index = 0 
                        self.stats[self.llm_player_id]["defaulted_move"] += 1
                        break
                    attempts += 1
                    selected_index = self.request_llm_action(actions)
            else:
                selected_index = self.request_user_action(actions)
            self.select_action(player_id, actions, selected_index, space)

            if actions[selected_index] != "End turn":
                self.print_player_state(player_id)
            else:
                break
            
            actions = self.get_valid_actions(player_id, space)

    def request_user_action(self, actions: List[str]):
        money = self.players[0]["money"]
        print(f"Player Money: ${money}")
        print("\nAvailable Actions: ")
        for index, action in enumerate(actions):
            print(f"{index}: {action}")
        selected_index = -1
        while True:
            try:
                selected_index = int(input("\nPlease select an action by typing a single number: "))
                if 0 <= selected_index < len(actions):
                        break
                else:
                    print(f"Error: Please enter number between 0 and {len(actions) - 1}")
            except ValueError:
                print("Error: Please enter a valid number")
        return selected_index
    
    def create_llm_context(self, actions):
        context = ""
        with open(f'prompts/{self.llm}_context.txt', 'r') as file:
            context = file.read()

        memory_summary = "Past 3 Actions:\n"
        for memory in self.llm_memory:
            new_net_worth = memory["new_net_worth"] if memory["new_net_worth"] is not None else memory["prev_net_worth"]
            effect = new_net_worth - memory["prev_net_worth"]
            memory_summary += f"Action: {memory['action']} | Effect on net worth: {effect:+} (${memory['new_net_worth']})\n"

        # useful variables
        # player = self.get_current_player()
        players_info = ""
        for player in self.players:
            self_label = ""
            if player == self.get_current_player():
                self_label = " (you)"
            current_pos = self.board[player['position']].name
            if player['position'] == 10:
                if player['in_jail']:
                    jail_status = " (In Jail)"
                else:
                    jail_status = " (Not in Jail)"
                current_pos += jail_status
            player_info = f"Player {player['id']}{self_label}:\nPosition: {current_pos} \nBalance: {player['money']} \nProperties Owned: \n"
            color_sets = {}

            for property in player["properties"]:
                if isinstance(property, Railroad):
                    if "railroad" not in color_sets:
                        color_sets["railroad"] = ([], 0, 4)
                    properties, color_owned, total_in_set = color_sets["railroad"]
                    property_name = property.name
                    if property.is_mortgaged:
                        property_name += " (mortgaged)"
                    properties.append(property.name)
                    color_owned += 1
                    color_sets["railroad"] = (properties, color_owned, total_in_set)
                elif isinstance(property, Utility):
                    if "utilities" not in color_sets:
                        color_sets["utilities"] = ([], 0, 2)
                    properties, color_owned, total_in_set = color_sets["utilities"]
                    property_name = property.name
                    if property.is_mortgaged:
                        property_name += " (mortgaged)"
                    properties.append(property.name)
                    color_owned += 1
                    color_sets["utilities"] = (properties, color_owned, total_in_set)
                else:
                    color = property.color_set
                    if color not in color_sets:
                        color_sets[color] = ([], 0, property.number_in_set)
                    properties, color_owned, total_in_set = color_sets[color]
                    property_name = f"{property.name}"
                    if property.is_mortgaged:
                        property_name += " (mortgaged)"
                    else:
                        property_name += f": ({property.number_of_houses} houses, {property.number_of_hotels} hotels)"
                    properties.append(property_name)
                    color_owned += 1
                    color_sets[color] = (properties, color_owned, total_in_set)
            
            for color_set in color_sets:
                properties, color_owned, total_in_set = color_sets[color_set]
                player_info += f"{color_set} ({color_owned}/{total_in_set} owned): ({', '.join(properties)}) \n"

            players_info += player_info + "\n "

        actions_desc = "Your selection MUST be a number from the list below. \n Available Actions: \n"
        for index, action in enumerate(actions):
            actions_desc += f"{index}: {action}\n"
        # prompt = context.replace("<INPUT>", f"\n{players_info}{actions_desc}")
        prompt = f"{context} \n{memory_summary} \nProperties Owned: \n{players_info}{actions_desc}"
        # prompt = f"{context} \nProperties Owned: \n{players_info}{actions_desc}"
        game_state = f"\n{players_info}{actions_desc}"
        return prompt, game_state

    def request_llm_action(self, actions):
        context, game_state = self.create_llm_context(actions)
        if not self.agent:
            return -1
        print("LLM Context:")  # Debugging
        print(context)  # Debugging
        # print(context)
        # print('Game State: ' + game_state)
        res = self.agent.query(context)
        try:
            json_object = json.loads(res)
        except json.JSONDecodeError as e:
            print(res)
            print(f"Invalid JSON: {e}")
            self.stats[self.llm_player_id]["invalid_json"] += 1
            return -1
        print("LLM Response")
        print(json_object)
        print("-------------------------")
        if not "selection" in json_object or not isinstance(json_object["selection"], int):
            self.stats[self.llm_player_id]["invalid_json"] += 1
            return -1
        selected_index = int(json_object["selection"])
        if 0 <= selected_index < len(actions):
            return selected_index
        self.stats[self.llm_player_id]["invalid_move"] += 1
        return -1
    
    def print_player_state(self, player_id: int):
        player = self.players[player_id]
        properties = []
        for property in player["properties"]:
            if property.is_mortgaged:
                properties.append(f"{property.name} (mortgaged)")
                continue
            if isinstance(property, Property):
                properties.append(f"{property.name} ({property.color_set}, {property.number_of_houses} houses, {property.number_of_hotels} hotels)")
            else:
                properties.append(f"{property.name}")
        summary = f"Player {player_id} has a total net worth of ${self.get_net_worth(player_id)}, can sell/mortgage everything for ${self.get_sell_worth(player_id)}, has ${player['money']} in cash, and owns the following properties: {', '.join(properties)}"
        #print(summary)

        return summary

    def display_board_state(self):
        img = Image.open("assets/board.png")
        draw = ImageDraw.Draw(img)

        def draw_dot(x, y, radius=5, color='red'):
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)

        for space in self.board:
            if space.coordinates:
                top_left = space.coordinates[0]
                bottom_right = space.coordinates[1]
                
                # Draw dots at all 4 corners
                draw_dot(top_left[0], top_left[1])      # Top-left
                draw_dot(bottom_right[0], top_left[1])  # Top-right
                draw_dot(top_left[0], bottom_right[1])  # Bottom-left
                draw_dot(bottom_right[0], bottom_right[1])  # Bottom-right

        # Save the modified image
        img.save("assets/dotted_board.png")

    def get_space_center(self, space):
        if not space.coordinates:
            return (0, 0)
        center_x = ((space.coordinates[0][0] + space.coordinates[1][0]) // 2)
        center_y = ((space.coordinates[0][1] + space.coordinates[1][1]) // 2)
        return (center_x, center_y)

    def draw_dice(self, draw):
        dice_1, dice_2 = self.last_dice_roll
        size = 100
        padding = size // 4
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 50)
        
        def draw_die(x, y, number):
            dot_radius = size // 10
            
            draw.rectangle([(x, y), (x + size, y + size)], 
                        fill='white', outline='black', width=2)

            dot_positions = {
                'top_left': (0.25, 0.25),
                'top_middle': (0.5, 0.25),
                'top_right': (0.75, 0.25),
                'middle_left': (0.25, 0.5),
                'center': (0.5, 0.5),
                'middle_right': (0.75, 0.5),
                'bottom_left': (0.25, 0.75),
                'bottom_middle': (0.5, 0.75),
                'bottom_right': (0.75, 0.75)
            }

            dot_patterns = {
                1: ['center'],
                2: ['top_right', 'bottom_left'],
                3: ['top_right', 'center', 'bottom_left'],
                4: ['top_left', 'top_right', 'bottom_left', 'bottom_right'],
                5: ['top_left', 'top_right', 'center', 'bottom_left', 'bottom_right'],
                6: ['top_left', 'top_right', 'middle_left', 'middle_right', 
                    'bottom_left', 'bottom_right']
            }

            for position in dot_patterns[number]:
                dot_x, dot_y = dot_positions[position]
                center_x = x + (dot_x * size)
                center_y = y + (dot_y * size)
                draw.ellipse([(center_x - dot_radius, center_y - dot_radius),
                            (center_x + dot_radius, center_y + dot_radius)],
                            fill='black')
        
        dice_1_x = 300 + padding
        dice_2_x = 300 + padding * 2 + size
        dice_y = 1550 + padding

        draw.text((dice_1_x, dice_y - 100), f"Player {self.current_player} Turn", fill='black', font=font)

        draw_die(dice_1_x, dice_y, dice_1)
        draw_die(dice_2_x, dice_y, dice_2)
    
    def draw_property_owners(self, property: PurchaseableProperty, property_index: int, draw, color):
        side = (property_index // 10) % 4
        (x1, y1), (x2, y2) = property.coordinates

        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if side == 0:
            fill_coords = (
                (x1, y2 - height/6),
                (x2, y2)
            )
        elif side == 1:
            fill_coords = (
                (x1, y1),
                (x1 + width/6, y2)
            )
        elif side == 2:
            fill_coords = (
                (x1, y1),
                (x2, y1 + height/6)
            )
        else:
            fill_coords = (
                (x2 - width/6, y1),
                (x2, y2)
            )

        draw.rectangle([fill_coords[0], fill_coords[1]], fill=color)
    
    def draw_mortgages(self, property: PurchaseableProperty, overlay_draw):
        overlay_color = (255, 0, 0, 100)
        overlay_draw.rectangle([property.coordinates[0], property.coordinates[1]], fill=overlay_color)

    def draw_construction(self, property: PurchaseableProperty, property_index: int, draw, color):
        if not hasattr(property, 'number_of_houses'):
            return
        side = (property_index // 10) % 4
        (x1, y1), (x2, y2) = property.coordinates
        num_houses = property.number_of_houses
        has_hotel = property.number_of_hotels == 1

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if side == 0:
            house_area = (
                (x1, y1),
                (x2, y1 + height/5)
            )
        elif side == 1:
            house_area = (
                (x2 - width / 5, y1),
                (x2, y2)
            )
        elif side == 2:
            house_area = (
                (x1, y2 - height / 5),
                (x2, y2)
            )
        else:
            house_area = (
                (x1, y1),
                (x1 + width / 5, y2)
            )
        house_size = max(width, height) / 12
        house_gap = house_size / 2
        hotel_width = house_size * 3
        hotel_height = house_size * 2
        if has_hotel:
            hotel_x = (house_area[0][0] + house_area[1][0]) / 2 - hotel_width / 2
            hotel_y = (house_area[0][1] + house_area[1][1]) / 2 - hotel_height / 2
            if side in (0, 2): 
                draw.rectangle([
                    (hotel_x, hotel_y),
                    (hotel_x + hotel_width, hotel_y + hotel_height)
                ], fill="red")
            else:
                draw.rectangle([
                    (hotel_x, hotel_y),
                    (hotel_x + hotel_height, hotel_y + hotel_width)
                ], fill="red")                
        else:
            if side in (1, 3):
                start_y = (house_area[0][1] + house_area[1][1]) / 2 - ((num_houses) * (house_size + house_gap) - house_gap) / 2
                start_x = (house_area[0][0] + house_area[1][0]) / 2 - house_size / 2

                for i in range(num_houses):
                    house_y = start_y + i * (house_size + house_gap)
                    draw.rectangle([
                        (start_x, house_y),
                        (start_x + house_size, house_y + house_size)
                    ], fill="green")
            else:
                start_x = (house_area[0][0] + house_area[1][0]) / 2 - ((num_houses) * (house_size + house_gap) - house_gap) / 2
                start_y = (house_area[0][1] + house_area[1][1]) / 2 - house_size / 2
                
                for i in range(num_houses):
                    house_x = start_x + i * (house_size + house_gap)
                    draw.rectangle([
                        (house_x, start_y),
                        (house_x + house_size, start_y + house_size)
                    ], fill="green")

    def draw_stats(self, draw):
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 50)
        x = 1100
        y = 300
        spacing = 50
        for player in self.players:
            id = player['id']
            draw.text((x, y), f"Player {id} Balance: {player['money']}", fill='black', font=font)
            y += spacing
            draw.text((x, y), f"Player {id} Net Worth: {self.get_net_worth(id)}", fill='black', font=font)
            y += spacing
    def save_board_image(self, turn_number):
        img = Image.open("assets/board.png").convert("RGBA")
        draw = ImageDraw.Draw(img)
        positions = defaultdict(list)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        self.draw_dice(draw)
        self.draw_stats(draw)

        for player in self.players:
            positions[player["position"]].append(player)
            color = "blue" if player["id"] == self.llm_player_id else "purple"
            for property in player["properties"]:
                self.draw_property_owners(property, self.board.index(property), draw, color)
                self.draw_construction(property, self.board.index(property), draw, color)
                if property.is_mortgaged:
                    self.draw_mortgages(property, overlay_draw)

        for position, players in positions.items():
            space = self.board[position]
            center_x, center_y = self.get_space_center(space)
            num_players = len(players)
            radius = 30
            if len(players) == 1:
                color = "blue" if players[0]["id"] == self.llm_player_id else "purple"
                draw.ellipse(
                    (
                        center_x - radius,
                        center_y - radius,
                        center_x + radius,
                        center_y + radius,
                    ),
                    fill=color,
                    outline="black",
                )
            else:
                for i, player in enumerate(players):
                    angle = (2 * math.pi / num_players) * i
                    offset_x = int(38 * math.cos(angle))
                    offset_y = int(38 * math.sin(angle))

                    color = "blue" if player["id"] == self.llm_player_id else "purple"
                    draw.ellipse(
                        (
                            center_x + offset_x - radius,
                            center_y + offset_y - radius,
                            center_x + offset_x + radius,
                            center_y + offset_y + radius,
                        ),
                        fill=color,
                        outline="black",
                    )
        
        img = Image.alpha_composite(img, overlay)
        os.makedirs("game_frames", exist_ok=True)
        img.save(f"game_frames/frame_{turn_number}.png")
        

def main():
    llm = "human"
    num_players = 2
    max_rounds = 100
    total_games = 10 #total games ran is actually 2x this since it runs total_games for each side

    game = MonopolyGame(num_players, llm_player_id=0, llm=llm)

    game.display_board_state()

    os.makedirs('game_results', exist_ok=True)
    results_file = os.path.join('game_results', f'{llm}_results_trials.txt')

    logging.basicConfig(
        filename=results_file,
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )

    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.flush = lambda: True

    with open(results_file, 'a') as file:
        player_wins = [0 for i in range(num_players)]
        for i in range(1, total_games + 1): # LLM going first
            game = MonopolyGame(num_players, llm_player_id=0, llm=llm)
            winner_id = game.play_game(max_rounds, i)
            player_wins[winner_id] += 1
        
        for i in range(len(player_wins)):
            if i == 0:
                logging.info(f"LLM won {player_wins[i]}/{total_games} games \n")
            else:
                logging.info(f"Bot won {player_wins[i]}/{total_games} games \n")
        
        player_wins = [0 for i in range(num_players)]
        for i in range(4, total_games + 1):  # LLM going second
            game = MonopolyGame(num_players, llm_player_id=1, llm=llm)
            winner_id = game.play_game(max_rounds, i)
            player_wins[winner_id] += 1
        
        for i in range(len(player_wins)):
            if i == 1:
                logging.info(f"LLM won {player_wins[i]}/{total_games} games \n")
            else:
                logging.info(f"Bot won {player_wins[i]}/{total_games} games \n")

if __name__=="__main__":
    main()
