from dataclasses import dataclass
from typing import Dict, List, Optional
import random
from collections import deque
import re
from collections import defaultdict
from llama_agent import Llama3_Agent
from mistral_agent import MistralAgent
import requests
import json

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
    is_mortgaged: bool = False
    owned_by: Optional[int] = None

@dataclass
class Utility:
    name: str
    price: int
    mortgage_value: int
    mortgage_fee: int
    is_mortgaged: bool = False
    owned_by: Optional[int] = None

@dataclass
class Tax:
    name: str
    type: str
    amount: int

@dataclass
class SpecialSpace:
    name: str

PurchaseableProperty = Property | Railroad | Utility

MONOPOLY_BOARD = [
    SpecialSpace("Go"),
    Property("Mediterranean Avenue", 60, [2, 10, 30, 90, 160, 250], 50, "brown", 2, 30, 33),
    SpecialSpace("Community Chest"),
    Property("Baltic Avenue", 60, [4, 20, 60, 180, 320, 450], 50, "brown", 2, 30, 33),
    Tax("Income Tax", "tax", 200),
    Railroad("Reading Railroad", 200, [25, 50, 100, 200], 100, 110),
    Property("Oriental Avenue", 100, [6, 30, 90, 270, 400, 550], 50, "light_blue", 3, 50, 55),
    SpecialSpace("Chance"),
    Property("Vermont Avenue", 100, [6, 30, 90, 270, 400, 550], 50, "light_blue", 3, 50, 55),
    Property("Connecticut Avenue", 120, [8, 40, 100, 300, 450, 600], 50, "light_blue", 3, 60, 66),
    SpecialSpace("Jail/Just Visiting"),
    Property("St. Charles Place", 140, [10, 50, 150, 450, 625, 750], 100, "pink", 3, 70, 77),
    Utility("Electric Company", 150, 75, 83),
    Property("States Avenue", 140, [10, 50, 150, 450, 625, 750], 100, "pink", 3, 70, 77),
    Property("Virginia Avenue", 160, [12, 60, 180, 500, 700, 900], 100, "pink", 3, 80, 88),
    Railroad("Pennsylvania Railroad", 200, [25, 50, 100, 200], 100, 110),
    Property("St. James Place", 180, [14, 70, 200, 550, 750, 950], 100, "orange", 3, 90, 99),
    SpecialSpace("Community Chest"),
    Property("Tennessee Avenue", 180, [14, 70, 200, 550, 750, 950], 100, "orange", 3, 90, 99),
    Property("New York Avenue", 200, [16, 80, 220, 600, 800, 1000], 100, "orange", 3, 100, 110),
    SpecialSpace("Free Parking"),
    Property("Kentucky Avenue", 220, [18, 90, 250, 700, 875, 1050], 150, "red", 3, 110, 121),
    SpecialSpace("Chance"),
    Property("Indiana Avenue", 220, [18, 90, 250, 700, 875, 1050], 150, "red", 3, 110, 121),
    Property("Illinois Avenue", 240, [20, 100, 300, 750, 925, 1100], 150, "red", 3, 120, 132),
    Railroad("B. & O. Railroad", 200, [25, 50, 100, 200], 100, 110),
    Property("Atlantic Avenue", 260, [22, 110, 330, 800, 975, 1150], 150, "yellow", 3, 130, 143),
    Property("Ventnor Avenue", 260, [22, 110, 330, 800, 975, 1150], 150, "yellow", 3, 130, 143),
    Utility("Water Works", 150, 75, 83),
    Property("Marvin Gardens", 280, [24, 120, 360, 850, 1025, 1200], 150, "yellow", 3, 140, 154),
    SpecialSpace("Go To Jail"),
    Property("Pacific Avenue", 300, [26, 130, 390, 900, 1100, 1275], 200, "green", 3, 150, 165),
    Property("North Carolina Avenue", 300, [26, 130, 390, 900, 1100, 1275], 200, "green", 3, 150, 165),
    SpecialSpace("Community Chest"),
    Property("Pennsylvania Avenue", 320, [28, 150, 450, 1000, 1200, 1400], 200, "green", 3, 160, 176),
    Railroad("Short Line", 200, [25, 50, 100, 200], 100, 110),
    SpecialSpace("Chance"),
    Property("Park Place", 350, [35, 175, 500, 1100, 1300, 1500], 200, "dark_blue", 2, 175, 193),
    Tax("Luxury Tax", "tax", 100),
    Property("Boardwalk", 400, [50, 200, 600, 1400, 1700, 2000], 200, "dark_blue", 2, 200, 220),
]

class MonopolyGame:
    def __init__(self, num_players: int, llm=None):
        self.num_players = num_players
        self.board = self._initialize_board()
        self.players = self._initialize_players()
        self.current_player = 0
        self.num_rounds = 0
        self.chance_cards = self._initialize_cards()
        self.community_chest_cards = self._initialize_cards()
        self.remaining_houses = 32
        self.remaining_hotels = 12 
        self.agent = self._initialize_llm(llm)

        # data log for RL
        self.game_data = []

    def _initialize_players(self):
        return [
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

    def _initialize_board(self):
        return MONOPOLY_BOARD

    def _initialize_cards(self):
        return deque(random.sample(range(16), 16))
    
    def _initialize_llm(self, llm):
        if llm == "llama3":
            return Llama3_Agent()
        if llm == "Mistral":
            return MistralAgent()
        print("player: ", llm)
        return None

    def roll_dice(self):
        dice_1 = random.randint(1, 6)
        dice_2 = random.randint(1, 6)
        double_rolled = True if dice_1 == dice_2 else False

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
        card = 4
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
        print()
    
    def purchase_property(self, player_id: int, property: PurchaseableProperty):
        self.players[player_id]["properties"].append(property)
        self.players[player_id]["money"] -= property.price
        property.owned_by = player_id

        print(f"Player {player_id} bought {property.name} for ${property.price}")
    
    def build_house(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
        for property in properties:
            if property.name == property_name:
                if property.number_of_houses < 4:
                    self.remaining_houses -= 1
                    property.number_of_houses += 1
                    player["money"] -= property.house_price
                else:
                    self.remaining_houses += 4
                    self.remaining_hotels -= 1
                    property.number_of_houses = 0
                    property.number_of_hotels = 1
                    player["money"] -= property.house_price

    def sell_house(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
        for property in properties:
            if property.name == property_name:
                if property.number_of_houses < 4:
                    self.remaining_houses -= 1
                    property.number_of_houses += 1
                    player["money"] -= property.house_price
                else:
                    self.remaining_houses += 4
                    self.remaining_hotels -= 1
                    property.number_of_houses = 0
                    property.number_of_hotels = 1
                    player["money"] -= property.house_price

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
        for property in properties:
            if property.name == property_name:
                property.is_mortgaged = True
                player["money"] += property.mortgage_value
                print(f"Player {player_id} mortgaged {property.name} for ${property.mortgage_value}")

    def unmortgage_property(self, player_id: int, property_name: str):
        player = self.players[player_id]
        properties = player["properties"]
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
        print(f"Player {player_1_id} paid ${rent} in rent to player {player_2_id}")
    
    def baseline_strategy(self, player_id: int, space):
        player = self.players[player_id]
        if isinstance(space, PurchaseableProperty) and space.owned_by is None and space.price < player["money"]:
            self.purchase_property(player_id, space)

        if player["in_jail"]:
            dice_1, dice_2, double_rolled = self.roll_dice()
            if player["get_out_of_jail_cards"] > 0:
                player["turns_in_jail"] = 0
                player["in_jail"] = False
                player["get_out_of_jail_cards"] -= 1
                print(f"Player {player_id} used a Get Out of Jail Free card")
                return (dice_1, dice_2, double_rolled)
            elif player["money"] >= 50:
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
                        print(f"Player {player_id} rolled {(dice_1, dice_2)} and stayed in jail")
                        player["turns_in_jail"] += 1
                        return (-1, -1, False)

    def get_valid_actions(self, player_id: int, space):
        player = self.players[player_id]
        properties = player["properties"]
        available_actions = []
        
        if isinstance(space, PurchaseableProperty) and space.owned_by is None and space.price < player["money"]:
            available_actions.append(f"Purchase {space.name} for ${space.price}")
        
        color_sets = defaultdict(list)
        complete_color_sets = []
        for property in properties:
            if property.is_mortgaged and player["money"] >= property.mortgage_fee:
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
                    if player["money"] >= property.house_price:
                        if num_houses == 5:
                            available_actions.append(f"Sell hotel on {property.name} for ${property.house_price / 2}")
                        elif num_houses > 0:
                            available_actions.append(f"Sell house on {property.name} for ${property.house_price / 2}")
        
        available_actions.append("End turn")
        
        return available_actions

    def select_action(self, player_id: int, actions: List[str], selected_index: int, space):
        action = actions[selected_index]
        action_type = action.split(" ")[0]

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
            pattern = r'^Build (house|hotel) on Mortgage ([A-Za-z]+(?:[.\s&]+[A-Za-z]+){0,4}) for \$(\d+(?:\.\d{2})?)$'
            match = re.match(pattern, action.strip())
            property_name = match.group(2)
            self.build_house(player_id, property_name)
        elif action_type == "Sell":
            pattern = r'^Sell (house|hotel) on Mortgage ([A-Za-z]+(?:[.\s&]+[A-Za-z]+){0,4}) for \$(\d+(?:\.\d{2})?)$'
            match = re.match(pattern, action.strip())
            property_name = match.group(2)
            self.sell_house(player_id, property_name)
        else:
            return

    def play_turn(self):
        player = self.get_current_player()
        player_id = player["id"]
        total_doubles = 0
        roll_again = True

        while roll_again:
            roll_again = False
            if self.players[player_id]["in_jail"]:
                if player_id == 0:
                    actions = self.get_jail_actions(player_id)
                    selected_index = self.request_action(actions)
                    dice_1, dice_2, double_rolled = self.select_jail_action(player_id, actions, selected_index)
                    if dice_1 == -1:
                        break
                else:
                    dice_1, dice_2, double_rolled = self.baseline_strategy(player_id, self.board[10])
                    if dice_1 == -1:
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

            if isinstance(space, PurchaseableProperty) and space.owned_by is not None and space.owned_by != player_id and not space.is_mortgaged:
                self.pay_rent(player_id, space.owned_by, space, (dice_1 + dice_2), multiplier)
            else:
                if player_id == 0:
                    selected_index = -1 #Where the LLM will input actions later
                    actions = self.get_valid_actions(player_id, space)
                    
                    while selected_index != len(actions) - 1:
                        selected_index = -1
                        if self.agent:
                            print("true")
                            while selected_index == -1:
                                selected_index = self.request_llm_action(actions)
                        else:
                            print("false")
                            selected_index = self.request_action(actions)
                        print(selected_index)
                        self.select_action(player_id, actions, selected_index, space)
                        actions = self.get_valid_actions(player_id, space)
                        self.print_player_state(player_id)
                else:
                    self.baseline_strategy(player_id, space) #Where the benchmark AI will select actions later 
            
            self.print_player_state(player_id)

        state = {
            "player_position": player["position"],
            "player_money": player["money"],
            "properties_owned": [p.name for p in player["properties"]],
            "in_jail": player["in_jail"],
            "remaining_houses": self.remaining_houses,
            "remaining_hotels": self.remaining_hotels
        }
        selected_action = "End turn"
        turn_data = {"state": state, "action": selected_action}
        self.game_data.append(turn_data)
        
        self.next_turn()

    def play_game(self, max_rounds: int):
        while self.num_rounds < max_rounds:
            self.play_turn()

        print(f"Game over after {self.num_rounds} rounds")
        for player in self.players:
            self.print_player_state(player["id"])
        
        # when the game is over save the data for learning
        with open('monopoly_data.json', 'w') as f:
            json.dump(self.game_data, f, indent=4)
        print("Game data saved to monopoly_data.json")

    def request_action(self, actions: List[str]):
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
        instruction = '''You are a professional monopoly player. Analyze the current game state below. Also discuss your plans for future turns and your strategy. Think about the pros and cons of each move, and use them to choose the most optimal action. Provide your response only with valid JSON following this specified format.\n{"reasons": explain the reasoning behind your decision and your long term strategy in less than 50 words, "selection": write your selection number here}. '''
        #not including example since it was making the llm output 2 jsons?
        example = '''This is one example output format. {"selection": 1, "reasons": "I choose to buy Indiana Avenue to complete the red color set, so I can start building houses for higher rent"}'''
        strategy = "Here are some strategy considerations. Mortgaging a property prevents it from collecting rent. When you unmortgage a property, it deducts the listed amount from your balance. As such, you should mortgage properties very carefully."
        # useful variables
        # player = self.get_current_player()
        players_info = ""
        for player in self.players:
            self_label = ""
            if player == self.get_current_player():
                self_label = " (you)"
            current_pos = self.board[player['position']].name
            player_info = f"Player {player['id']}{self_label}:\n Position: {current_pos} \n Balance: {player['money']} \n"
            property_listings = "Properties Owned: \n"
            for property in player["properties"]:
                houses_desc = ""
                color_desc = ""
                mortgaged = ""
                if property.is_mortgaged:
                    mortgaged = " (mortgaged)"
                if type(property) == Property:
                    color_desc = f"({property.color_set})"
                    if (property.number_of_hotels > 0):
                        houses_desc = f"{property.number_of_hotels} hotel"
                    else:
                        houses_desc = f"{property.number_of_houses} houses"
                desc = f"{property.name} {color_desc}{mortgaged} {houses_desc} \n"
                property_listings += desc
            players_info += f"{player_info} {property_listings} \n"
        actions_desc = "Available Actions: \n"
        for index, action in enumerate(actions):
            actions_desc += f"{index}: {action}\n"
        prompt = f"{instruction} \n {strategy} \n {players_info} {actions_desc}"
        return prompt

    def request_llm_action(self, actions):
        context = self.create_llm_context(actions)
        
        print(context)
        res = self.agent.query(context)
        try:
            json_object = json.loads(res)
            if "selection" in json_object:
                selected_index = int(json_object["selection"])
            if 0 <= selected_index < len(actions):
                return selected_index
            print("Invalid selection received")
            return -1
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return -1
        print(json_object)
        if not "selection" in json_object:
            return -1
        selected_index = int(json_object["selection"])
        if 0 <= selected_index < len(actions):
            return selected_index
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
        print(f"Player {player_id} has ${player['money']} and owns the following properties: {', '.join(properties)}")

def main():
    # game = MonopolyGame(2, "llama3")
    game = MonopolyGame(num_players=2, llm="Mistral")
    game.play_game(max_rounds=1)

if __name__=="__main__":
    main()