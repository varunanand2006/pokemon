import random
from move_database import move_list, items, tm, battle_items, evolve_into, evolve_level
import datetime

type_chart = {"normal": {"weakness": ["fighting"], "resistance": [], "immunity": ["ghost"]},
              "grass": {"weakness": ["fire", "ice", "poison", "bug", "flying"],
                        "resistance": ["grass", "water", "ground", "electric"], "immunity": []},
              "fire": {"weakness": ["water", "rock", "ground"],
                       "resistance": ["grass", "fire", "ice", "steel", "fairy", "bug"], "immunity": []},
              "water": {"weakness": ["grass", "electric"], "resistance": ["water", "fire", "ice", "steel"],
                        "immunity": []},
              "electric": {"weakness": ["ground"], "resistance": ["electric", "steel"], "immunity": []},
              "dragon": {"weakness": ["dragon", "ice", "fairy"], "resistance": ["water", "fire", "grass", "electric"],
                         "immunity": []},
              "flying": {"weakness": ["electric", "ice", "rock"], "resistance": ["grass", "fighting", "bug"],
                         "immunity": ["ground"]},
              "poison": {"weakness": ["ground", "psychic"], "resistance": ["grass", "fighting", "poison", "fairy"],
                         "immunity": []},
              "bug": {"weakness": ["fire", "flying", "rock"], "resistance": ["grass", "fighting", "ground"],
                      "immunity": []},
              "fighting": {"weakness": ["psychic", "fairy", "flying"], "resistance": ["bug", "rock", "dark"],
                           "immunity": []},
              "ice": {"weakness": ["fire", "rock", "fighting", "steel"], "resistance": ["ice"], "immunity": []},
              "ground": {"weakness": ["water", "grass", "ice"], "resistance": ["poison", "rock"],
                         "immunity": ["electric"]},
              "rock": {"weakness": ["water", "grass", "steel", "fighting", "ground"],
                       "resistance": ["normal", "fire", "poison", "flying"], "immunity": []},
              "ghost": {"weakness": ["ghost", "dark"], "resistance": ["poison", "bug"],
                        "immunity": ["normal", "fighting"]},
              "dark": {"weakness": ["fighting", "fairy", "bug"], "resistance": ["ghost", "dark"],
                       "immunity": ["psychic"]}, "steel": {"weakness": ["fire", "fighting", "ground"],
                                                           "resistance": ["dragon", "fairy", "normal", "grass", "ice",
                                                                          "flying", "psychic", "bug", "rock",
                                                                          "steel"], "immunity": ["poison"]},
              "fairy": {"weakness": ["steel", "poison"], "resistance": ["fighting", "bug", "dark"],
                        "immunity": ["dragon"]},
              "psychic": {"weakness": ["bug", "dark", "ghost"], "resistance": ["fighting", "psychic"], "immunity": []}}


def printer_outer(message_1, message_2, chars):
    return message_1 + " " * (chars - len(message_1)) + message_2


def pokedex_decoder():
    file = open("pokedex", "r")
    txt = file.read()
    file.close()
    list_of_pokemon = txt.split("\n")[:-1]
    pokedex = {}
    for item in list_of_pokemon:
        pokemon = item.split("|")
        name = pokemon[0]
        poke_type = pokemon[1].split(", ")
        move = pokemon[2].split(", ")
        stats = pokemon[3].split(", ")
        ability = pokemon[4]
        stats = {"hp": int(stats[0]), "attack": int(stats[1]), "defense": int(stats[2]), "s_attack": int(stats[3]),
                 "s_defense": int(stats[4]), "speed": int(stats[5])}
        pokedex[name] = {"name": name, "type": poke_type, "moves": move, "stats": stats, "ability": ability}
    return pokedex


def check_type(attk_type, def_type):
    type_mult = 1
    for typing in def_type:
        if attk_type in type_chart[typing]["weakness"]:
            type_mult *= 2
        elif attk_type in type_chart[typing]["resistance"]:
            type_mult /= 2
        elif attk_type in type_chart[typing]["immunity"]:
            type_mult *= 0
    return type_mult

class Trainer:
    def __init__(self, trainer_file):
        self.file = trainer_file
        self.decoder()
        self.create_pokemon()
        self.bag = Bag(self.item_bag, self.money)

    def encoder(self):
        items = [self.name + "\n", str(self.level) + "\n", str(self.bag.money) + "\n"]
        return_string = ""
        for item in self.bag.bag:
            return_string += item + ":" + str(self.bag.bag[item]) + ","
        items.append(return_string[:-1] + "\n")

        def encode_pokemon(pokemon):
            def list_is(list):
                return_list = []
                for item in list:
                    return_list.append(str(item))
                return return_list

            info_list = [pokemon.name, ",".join(pokemon.type), ",".join(pokemon.moveset), ",".join(list(list_is(pokemon.base_stats.values()))), pokemon.ability, str(pokemon.health), ",".join(pokemon.status_condition), pokemon.held_item,
                         str(pokemon.level), ",".join(list_is(pokemon.EVs)), ",".join(list_is(pokemon.IVs)), str(pokemon.exp), pokemon.nature, pokemon.nickname, str(pokemon.friendship), pokemon.ball_caught_in, pokemon.gender]
            return "|".join(info_list)

        pokemon_list = []
        for pokemon in self.pokemon_box:
            pokemon_list.append(encode_pokemon(pokemon))
        items.append("\n".join(pokemon_list))
        file = open(self.file, "w")
        file.write("\split\n".join(items))
        file.close()
        return "\split\n".join(items)

    def decoder(self):
        file = open(self.file, "r")
        items = file.read().split("\split")
        file.close()
        self.name = items[0].replace("\n", "")
        self.level = int(items[1].replace("\n", ""))
        self.money = int(items[2].replace("\n", ""))
        self.item_bag = {}
        for item in items[3].replace("\n", "").split(","):
            self.item_bag[item.split(":")[0]] = int(item.split(":")[1])
        trainer_pokemon = items[4][1:].split("\n")

        def decode_pokemon(str):
            info = str.split("|")
            return {"name": info[0], "types": list(info[1].split(",")), "moves": list(info[2].split(",")),
                    "stats": list(info[3].split(",")), "ability": info[4], "current hp": int(info[5]),
                    "status condition": list(info[6].split(",")), "held item": info[7], "level": int(info[8]),
                    "EVs": list(info[9].split(",")), "IVs": list(info[10].split(",")), "EXP": int(info[11]),
                    "nature": info[12], "nickname": info[13], "friendship": int(info[14]), "ball caught in": info[15], "gender": info[16]}

        self.pokemon_list = []
        for pokemon in trainer_pokemon:
            self.pokemon_list.append(decode_pokemon(pokemon))

    def create_pokemon(self):
        self.pokemon_box = []
        for item in self.pokemon_list:
            self.pokemon_box.append(
                Pokemon(item["name"], item["moves"], item["ability"], item["status condition"], item["held item"],
                        item["level"], item["EXP"], item["EVs"], item["IVs"], item["nature"], item["nickname"], item["friendship"], item["ball caught in"], item["gender"]))

    def add_to_box(self, pokemon):
        self.pokemon_box.append(pokemon)
        self.encoder()

    def catch(self, pokemon, ball):
        if ball == "friend ball":
            pokemon.friendship = 200
        if ball == "heal ball":
            pokemon.health = pokemon.pokemon_stats["hp"]
            pokemon.status_condition = []



    def print_pokemon_box(self):
        for pokemon in self.pokemon_box:
            print(pokemon)

    def use_tm(self):
        while True:
            count = 1
            for pokemon in self.pokemon_box:
                print(str(count) + ": " +
                      printer_outer(
                          printer_outer("Nickname: {}".format(pokemon.nickname), "Species: {}".format(pokemon.name),
                                        30),
                          printer_outer("Level: {}".format(pokemon.level), "Held Item: {}".format(pokemon.held_item),
                                        15), 55)
                      + "\n" + printer_outer("Stats: {}".format(list(pokemon.pokemon_stats.values())),
                                             "Moves: {}".format(pokemon.moveset), 40) + "\n"
                      )
                count += 1
            chosen_pokemon = input(
                "Which pokemon would you like to tm?(1 - {}, [enter] to stop)".format(len(self.pokemon_box)))
            if chosen_pokemon == "":
                break
            try:
                print("-" * 100)
                chosen_pokemon = int(chosen_pokemon) - 1
                print("Name: {},          Moves: {}".format(self.pokemon_box[chosen_pokemon].name,
                                                            self.pokemon_box[chosen_pokemon].moveset))
                print("\nTMs:    ", end="")
                for item in tm:
                    if self.pokemon_box[chosen_pokemon].name in tm[item]["learnable"]:
                        if tm[item]["name"] not in self.pokemon_box[chosen_pokemon].moveset:
                            print(item.title(), end=", ")
                print("")
                tm_input = input("Which tm would you like to use?(Enter name)")
                if tm_input not in tm:
                    print("Choose a valid tm!")
                elif self.pokemon_box[chosen_pokemon].name not in tm[tm_input]["learnable"]:
                    print("Choose a tm from the list!")
                else:
                    move_replace = input("Which move would you like to replace? (In numbers 1-4): ")
                    try:
                        self.pokemon_box[chosen_pokemon].moveset[int(move_replace) - 1] = tm_input
                        print("The tm worked!")
                    except:
                        print("The tm did not work! Try putting in a number 1-4. ")
            except:
                print("Enter a number value!")

            def tm_assigner(pokemon, tm):
                if pokemon["name"] not in tm["learnable"]:
                    print("This pokemon cannot learn this move! ")
                    return pokemon
                print(printer_outer(
                    printer_outer("Pokemon: " + pokemon["name"], "Type: " + ", ".join(pokemon["type"]), 25),
                    "Moves: " + ", ".join(pokemon["moves"]), 60))
                move_replace = input("Which move would you like to replace? (In numbers 1-4): ")
                try:
                    pokemon["moves"][int(move_replace) - 1] = tm["name"]
                except:
                    print("The tm did not work! Try putting in a number 1-4. ")
                return pokemon

    def swap_items(self):
        while True:
            count = 1
            for pokemon in self.pokemon_box:
                print(str(count) + ": " +
                      printer_outer(
                          printer_outer("Nickname: {}".format(pokemon.nickname), "Species: {}".format(pokemon.name),
                                        30),
                          printer_outer("Level: {}".format(pokemon.level), "Held Item: {}".format(pokemon.held_item),
                                        15), 55)
                      + "\n" + printer_outer("Stats: {}".format(list(pokemon.pokemon_stats.values())),
                                             "Moves: {}".format(pokemon.moveset), 40) + "\n"
                      )
                count += 1
            chosen_pokemon = input(
                "Which pokemon would you like to swap items?(1 - {}, [enter] to stop)".format(len(self.pokemon_box)))
            if chosen_pokemon == "":
                break
            try:
                print("-" * 100)
                chosen_pokemon = int(chosen_pokemon) - 1
                print("Name: {},          Held Item: {}".format(self.pokemon_box[chosen_pokemon].name,
                                                            self.pokemon_box[chosen_pokemon].held_item))
                print(self.bag.bag)
                tm_input = input("Which item would you like to assign?(Enter name)")
                if tm_input not in items:
                    print("Choose a valid item!\n")
                elif tm_input not in self.bag.bag:
                    print("Choose an item in your bag!\n")
                else:
                    held_item = self.pokemon_box[chosen_pokemon].held_item
                    try:
                        if self.bag.remove_from_bag(tm_input, 1) == False:
                            print("Not enough of item in bag!\n")
                        else:
                            self.pokemon_box[chosen_pokemon].held_item = tm_input
                            self.bag.add_to_bag(held_item, 1)
                            print("Items swapped!\n")
                    except:
                        print("Error occured!\n")
            except:
                print("Enter a number value!\n")

    def name_nickname(self):
        while True:
            count = 1
            for pokemon in self.pokemon_box:
                print(str(count) + ": " +
                      printer_outer(
                          printer_outer("Nickname: {}".format(pokemon.nickname), "Species: {}".format(pokemon.name),
                                        30),
                          printer_outer("Level: {}".format(pokemon.level), "Held Item: {}".format(pokemon.held_item),
                                        15), 55)
                      + "\n" + printer_outer("Stats: {}".format(list(pokemon.pokemon_stats.values())),
                                             "Moves: {}".format(pokemon.moveset), 40) + "\n"
                      )
                count += 1
            chosen_pokemon = input(
                "Which pokemon would you like to name?(1 - {}, [enter] to stop)".format(len(self.pokemon_box)))
            if chosen_pokemon == "":
                break
            try:
                print("-" * 100)
                chosen_pokemon = int(chosen_pokemon) - 1
                print("Name: {},          Nickname: {}".format(self.pokemon_box[chosen_pokemon].name,
                                                            self.pokemon_box[chosen_pokemon].nickname))
                nickname = input("What is the new nickname?(Enter name)")
                if len(nickname) > 20:
                    print("Nickname longer than 20 characters!\n")
                elif "|" in nickname or "\split" in nickname:
                    print("Invalid nickname; cannot use '|'\n")
                else:
                    self.pokemon_box[chosen_pokemon].nickname = nickname
                    print("Pokemon named!\n")
            except:
                print("Enter a number value!\n")

    def choose_pokemon(self):
        print("Trainer: {}".format(self.name))
        while True:
            count = 1
            for pokemon in self.pokemon_box:
                print(str(count) + ": " +
                      printer_outer(
                          printer_outer("Nickname: {}".format(pokemon.nickname), "Species: {}".format(pokemon.name),
                                        30),
                          printer_outer("Level: {}".format(pokemon.level), "Held Item: {}".format(pokemon.held_item),
                                        15), 55)
                      + "\n" + printer_outer("Stats: {}".format(list(pokemon.pokemon_stats.values())),
                                             "Moves: {}".format(pokemon.moveset), 40) + "\n"
                      )
                count += 1
            chosen_pokemon = input(
                "Which pokemon would you like to add to the team?(1 - {}, [enter] to stop)".format(len(self.pokemon_box)))
            try:
                print("-" * 100)
                chosen_pokemon = int(chosen_pokemon) - 1
                print("Name: {},          Nickname: {}".format(self.pokemon_box[chosen_pokemon].name, self.pokemon_box[chosen_pokemon].nickname))
                return self.pokemon_box[chosen_pokemon]
            except:
                print("Enter a number value!\n")

class Pokemon:
    def __init__(self, name, moveset, ability, status_condition, held_item, level, exp, EVs, IVs, nature, nickname, friendship = 0, pokeball = "pokeball", gender = "None"):
        self.name = name
        self.type = self.find_in_pokedex()["type"]
        self.moveset = moveset
        self.ability = ability
        self.status_condition = status_condition
        if self.status_condition == [[]] or self.status_condition == [""]:
            self.status_condition = []
        self.held_item = held_item
        self.level = int(level)
        self.exp = int(exp)
        self.EVs = EVs
        self.IVs = IVs
        self.nature = nature
        self.nickname = nickname
        self.friendship = friendship
        self.ball_caught_in = pokeball
        self.gender = gender
        self.base_stats = self.find_in_pokedex()["stats"]
        self.all_stats()
        self.health = self.pokemon_stats["hp"]

    def printer_outer(self, message_1, message_2, chars):
        return message_1 + " " * (chars - len(message_1)) + message_2

    def pokedex_decoder(self):
        file = open("pokedex", "r")
        txt = file.read()
        file.close()
        list_of_pokemon = txt.split("\n")[:-1]
        pokedex = {}
        for item in list_of_pokemon:
            pokemon = item.split("|")
            name = pokemon[0]
            poke_type = pokemon[1].split(", ")
            move = pokemon[2].split(", ")
            stats = pokemon[3].split(", ")
            ability = pokemon[4]
            stats = {"hp": int(stats[0]), "attack": int(stats[1]), "defense": int(stats[2]), "s_attack": int(stats[3]),
                     "s_defense": int(stats[4]), "speed": int(stats[5])}
            pokedex[name] = {"name": name, "type": poke_type, "moves": move, "stats": stats, "ability": ability}
        return pokedex

    def find_in_pokedex(self):
        for item in self.pokedex_decoder():
            if self.name == item:
                return self.pokedex_decoder()[item]

    def take_damage(self, damage):
        self.health -= damage
        return self.hp_check()

    def heal(self, heal):
        self.health += heal
        self.hp_check()

    def hp_check(self):
        if self.health <= 0:
            self.health = 0
            return "fainted"
        elif self.health > self.pokemon_stats["hp"]:
            self.health = self.pokemon_stats["hp"]

    def add_status_condition(self, condition):
        if condition in self.status_condition:
            return None
        elif condition in ["toxic"] and "poisoned" in self.status_condition:
            condition.remove("poisoned")
            condition.append("toxic")
        else:
            self.status_condition.append(condition)

    def remove_status_condition(self, condition):
        if condition in self.status_condition:
            self.status_condition.remove(condition)
        elif condition == ["all"] or condition == "all":
            self.status_condition = []
        else:
            return False

    def add_held_item(self, item):
        self.held_item = str(item)

    def remove_held_item(self):
        self.held_item = ""

    def all_stats(self):
        def nature_mult(stat_selected, pkmn_nature):
            def nature_calc(pokmn_nature):
                inc_natures = {
                    "attack": ["hardy", "lonely", "adament", "naughty", "brave"],
                    "defense": ["bold", "docile", "impish", "lax", "relaxed"],
                    "s_attack": ["modest", "mild", "bashful", "rash", "quiet"],
                    "s_defense": ["calm", "gentle", "careful", "quirky", "sassy"],
                    "speed": ["timid", "hasty", "jolly", "naive", "serious"]
                }

                dec_natures = {
                    "attack": ["hardy", "bold", "modest", "calm", "timid"],
                    "defense": ["lonely", "docile", "mild", "gentle", "hasty"],
                    "s_attack": ["adament", "impish", "bashful", "careful", "jolly"],
                    "s_defense": ["naughty", "lax", "rash", "quirky", "naive"],
                    "speed": ["brave", "relaxed", "quiet", "sassy", "serious"],
                }
                inc_stat = "none"
                dec_stat = "none"
                for stat in inc_natures.keys():
                    for nature in inc_natures[stat]:
                        if nature == pokmn_nature:
                            inc_stat = stat
                for stat in dec_natures.keys():
                    for nature in dec_natures[stat]:
                        if nature == pokmn_nature:
                            dec_stat = stat
                return inc_stat, dec_stat

            increased_stat, decreased_stat = nature_calc(pkmn_nature)
            if increased_stat == decreased_stat:
                return 1
            else:
                if stat_selected == increased_stat:
                    return 1.1
                elif stat_selected == decreased_stat:
                    return 0.9
                else:
                    return 1

        HP = int(0.01 * (2 * int(self.base_stats["hp"]) + int(self.IVs[0]) + int(
            self.EVs[0]) / 4) * self.level) + self.level + 10
        Attack = int(((0.01 * (2 * int(self.base_stats["attack"]) + int(self.IVs[1]) + int(self.EVs[
                                                                                               1]) / 4) * self.level) + 5) * nature_mult(
            "attack", self.nature))
        Defense = int(((0.01 * (2 * int(self.base_stats["defense"]) + int(self.IVs[2]) + int(self.EVs[
                                                                                                 2]) / 4) * self.level) + 5) * nature_mult(
            "defense", self.nature))
        Special_Attack = int(((0.01 * (2 * int(self.base_stats["s_attack"]) + int(self.IVs[3]) + int(self.EVs[
                                                                                                         3]) / 4) * self.level) + 5) * nature_mult(
            "s_attack", self.nature))
        Special_Defense = int(((0.01 * (2 * int(self.base_stats["s_defense"]) + int(self.IVs[4]) + int(self.EVs[
                                                                                                           4]) / 4) * self.level) + 5) * nature_mult(
            "s_defense", self.nature))
        Speed = int(((0.01 * (
                2 * int(self.base_stats["speed"]) + int(self.IVs[5]) + int(
            self.EVs[5]) / 4) * self.level) + 5) * nature_mult(
            "speed", self.nature))
        self.pokemon_stats = {"hp": HP, "attack": Attack, "defense": Defense, "s_attack": Special_Attack,
                              "s_defense": Special_Defense, "speed": Speed}

    def experience_gain(self, defeated_pokemon):
        exp_dict = {
            "venusaur": 263,
            "charizard": 267,
            "blastoise": 265,
            "beedrill": 198,
            "pidgeot": 240,
            "pikachu": 112,
            "raichu": 243,
            "persian": 154,
            "poliwrath": 255,
            "alakazam": 250,
            "machamp": 253,
            "victreebel": 245,
            "golem": 248,
            "magneton": 163,
            "gengar": 250,
            "exeggutor": 186,
            "rhydon": 170,
            "chansey": 395,
            "pinsir": 175,
            "tauros": 172,
            "gyarados": 189,
            "lapras": 187,
            "vaporeon": 184,
            "jolteon": 184,
            "flareon": 184,
            "aerodactyl": 180,
            "snorlax": 189,
            "articuno": 290,
            "zapdos": 290,
            "moltres": 290,
            "dragonite": 300,
            "mewtwo": 340,
            "mew": 300,
            "meganium": 263,
            "typhlosion": 267,
            "feraligatr": 265,
            "crobat": 268,
            "ampharos": 255,
            "espeon": 184,
            "umbreon": 184,
            "steelix": 179,
            "scizor": 175,
            "heracross": 175,
            "piloswine": 158,
            "skarmory": 163,
            "kingdra": 270,
            "blissey": 635,
            "tyranitar": 300,
            "celebi": 300,
            "sceptile": 265,
            "blaziken": 265,
            "swampert": 268,
            "ludicolo": 240,
            "shiftry": 240,
            "gardevoir": 259,
            "aggron": 265,
            "manectric": 166,
            "flygon": 260,
            "altaria": 172,
            "walrein": 265,
            "salamence": 300,
            "metagross": 300,
            "latias": 300,
            "latios": 300,
            "kyogre": 335,
            "groudon": 335,
            "rayquaza": 340,
            "jirachi": 300,
            "deoxys": 300,
            "deoxys defense": 300,
            "deoxys speed": 300,
            "deoxys attack": 300,
            "toxicroak": 172,
            "lucario": 184,
            "weavile": 179,
            "togekiss": 273,
            "ice calyrex": 300,
            "shadow calyrex": 300
        }
        if defeated_pokemon.name not in exp_dict:
            b = 50
        else:
            b = exp_dict[defeated_pokemon.name]
        if self.held_item == "lucky egg":
            e = 1.5
        else:
            e = 1
        f = 1
        Lp = self.level
        L = defeated_pokemon.level
        p = 1
        s = 1
        t = 1
        v = 1
        self.exp += int(((b * L * f * v) / (5 * s) * ((2 * L + 10) / (L + Lp + 10)) ** 2.5) * t * e * p)

    def xp_to_next_lvl(self):
        exp_group = {
            "venusaur": "medium slow",
            "charizard": "medium slow",
            "blastoise": "medium slow",
            "beedrill": "medium fast",
            "pidgeot": "medium slow",
            "pikachu": "medium fast",
            "raichu": "medium fast",
            "persian": "medium fast",
            "poliwrath": "medium slow",
            "alakazam": "medium slow",
            "machamp": "medium slow",
            "victreebel": "medium slow",
            "golem": "medium slow",
            "magneton": "medium fast",
            "gengar": "medium slow",
            "exeggutor": "slow",
            "rhydon": "slow",
            "chansey": "fast",
            "pinsir": "slow",
            "tauros": "slow",
            "gyarados": "slow",
            "lapras": "slow",
            "vaporeon": "medium fast",
            "jolteon": "medium fast",
            "flareon": "medium fast",
            "aerodactyl": "slow",
            "snorlax": "slow",
            "articuno": "slow",
            "zapdos": "slow",
            "moltres": "slow",
            "dragonite": "slow",
            "mewtwo": "slow",
            "mew": "medium slow",
            "meganium": "medium slow",
            "typhlosion": "medium slow",
            "feraligatr": "medium slow",
            "crobat": "medium fast",
            "ampharos": "medium slow",
            "espeon": "medium fast",
            "umbreon": "medium fast",
            "steelix": "medium fast",
            "scizor": "medium fast",
            "heracross": "slow",
            "piloswine": "slow",
            "skarmory": "slow",
            "kingdra": "medium fast",
            "blissey": "fast",
            "tyranitar": "slow",
            "celebi": "slow",
            "sceptile": "medium slow",
            "blaziken": "medium slow",
            "swampert": "medium slow",
            "ludicolo": "medium slow",
            "shiftry": "medium slow",
            "gardevoir": "slow",
            "aggron": "slow",
            "manectric": "slow",
            "flygon": "medium slow",
            "altaria": "erratic",
            "walrein": "medium slow",
            "salamence": "slow",
            "metagross": "slow",
            "latias": "slow",
            "latios": "slow",
            "kyogre": "slow",
            "groudon": "slow",
            "rayquaza": "slow",
            "jirachi": "slow",
            "deoxys": "slow",
            "deoxys defense": "slow",
            "deoxys speed": "slow",
            "deoxys attack": "slow",
            "toxicroak": "medium fast",
            "lucario": "medium slow",
            "weavile": "medium slow",
            "togekiss": "fast",
            "ice calyrex": "slow",
            "shadow calyrex": "slow"
        }
        if self.name not in exp_group:
            try:
                if self.name in evolve_into:
                    if evolve_into[self.name] in exp_group:
                        exp_group = exp_group[evolve_into[self.name]]
                    elif evolve_into[evolve_into[self.name]] in exp_group:
                        exp_group = exp_group[evolve_into[evolve_into[self.name]]]
            except:
                group = "medium fast"
        else:
            group = exp_group[self.name]
        n = self.level
        if group == "erratic":
            if self.level < 50:
                return (n ** 3) * (100 - n) // 50
            elif 50 <= self.level < 68:
                return (n ** 3) * (150 - n) // 100
            elif 68 <= self.level < 98:
                return (n ** 3) * ((1911 - 10 * n) / 3) // 500
            elif self.level >= 98:
                return (n ** 3) * (160 - n) // 100
        elif group == "fast":
            return 4 * n ** 3 // 5
        elif group == "medium fast":
            return n ** 3
        elif group == "medium slow":
            return int((6 / 5 * (n ** 3)) - (15 * (n ** 2)) + (100 * n) - 140)
        elif group == "slow":
            return 5 * (n ** 3) // 4
        elif group == "fluctuating":
            if self.level < 15:
                return int((n ** 3) * (((n + 1) / 3) + 24) // 50)
            elif 15 <= self.level < 36:
                return int((n ** 3) * (n + 14) // 50)
            elif self.level >= 36:
                return int((n ** 3) * ((n / 2) + 32) // 50)

    def level_up(self, opponent_pokemon):
        self.experience_gain(opponent_pokemon)
        print(self.xp_to_next_lvl())
        while self.exp >= self.xp_to_next_lvl():
            self.exp -= self.xp_to_next_lvl()
            if self.level < 100:
                self.level += 1
                self.all_stats()
                print(self.name + " leveled up to level " + str(self.level))
        return self.level

    def evolve(self):
        if self.name not in evolve_into:
            return None
        if self.level >= evolve_level[self.name]:
            if type(evolve_into[self.name]) == list:
                evolve_name = random.choice(evolve_into[self.name])
            else:
                evolve_name = evolve_into[self.name]
            if self.name == self.nickname:
                self.nickname = evolve_name
            self.name = evolve_name
            self.base_stats = self.find_in_pokedex()["stats"]
            self.all_stats()
            self.type = self.find_in_pokedex()["type"]
            self.health = self.pokemon_stats["hp"]
            print("Your {} evolved into a {}!".format(self.nickname, self.name))
            return self

    def pokeball_catch_rate(self, user_pokemon, ball, turn = 0, location = "surface"):
        # determining pokeball effectiveness
        pokeball = {"pokeball": 1, "great ball": 1.5, "ultra ball": 2, "heal ball": 1, "luxury ball": 1}
        if ball in pokeball:
            pokeball_rate = pokeball[ball]
        else:
            pokeball_rate = 1
        if ball == "master ball":
            return (1000000000, ball)
        if ball == "dream ball":
            if "asleep" in self.status_condition:
                pokeball_rate = 4
        elif ball == "level ball":
            if self.level > user_pokemon.level and self.level <= 2 * user_pokemon.level:
                pokeball_rate = 2
            elif self.level > 2 * user_pokemon.level and self.level <= 4 * user_pokemon.level:
                pokeball_rate = 4
            elif self.level > 4 * user_pokemon.level:
                pokeball_rate = 8
        elif ball == "net ball" and ("water" in self.type or "bug" in self.type):
            pokeball_rate = 3.5
        elif ball == "quick ball" and turn == 1:
            pokeball_rate = 5
        elif ball == "timer ball":
            pokeball_rate = (turn + 10) / 10
        elif ball == "dusk ball" and location in ("cave", "underground"):
            pokeball_rate = 3.5
        elif ball == "dive ball" and location in ("sea", "underwater"):
            pokeball_rate = 3.5
        elif ball == "lure ball" and location == "fishing":
            pokeball_rate = 4
        elif ball == "fast ball" and self.pokemon_stats["speed"] >= 100:
            pokeball_rate = 4
        return (pokeball_rate, ball)


    def print_moveset(self):
        return_string = ""
        for item in self.moveset:
            return_string += self.printer_outer(
                self.printer_outer("Move: {}".format(item), "Type: {}".format(move_list[item]["type"]), 30),
                self.printer_outer("Catagory: {}".format(move_list[item]["c_type"]),
                                   "Power: {}".format(move_list[item]["power"]), 25), 50) + "\n"
        return return_string[:-1]

    def use_berry(self, berry):
        if berry == "oran berry":
            self.heal(10)
            self.remove_held_item()
            return True
        elif berry == "lum berry":
            self.remove_status_condition("all")
            self.remove_held_item()
            return True
        elif berry == "sitrus berry":
            self.heal(self.pokemon_stats["hp"] // 4)
            self.remove_held_item()
            return True

    def __repr__(self):
        return """Nickname: {}, Name: {}, Types: {}, Moves: {}, Stats: {}""".format(self.nickname, self.name, self.type,
                                                                                    self.moveset, self.pokemon_stats)


class Battle:
    def __init__(self, file1 = "trainer_info", file2 = "trainer_info"):
        # regarding trainers
        self.trainer_1 = Trainer(file1)
        self.trainer_2 = Trainer(file2)
        self.trainer_1_name = self.trainer_1.name
        self.trainer_2_name = self.trainer_2.name
        self.p1_bag = self.trainer_1.bag
        self.p2_bag = self.trainer_2.bag
        self.p1_box = self.trainer_1.pokemon_box
        self.p2_box = self.trainer_2.pokemon_box
        self.initialize_teams(2)

        # regarding pokemon stats


        # sets boosts
        self.p1_boosts = {"attack": 0, "defense": 0, "s_attack": 0, "s_defense": 0, "accuracy": 0, "evasion": 0,
                          "speed": 0}
        self.p2_boosts = {"attack": 0, "defense": 0, "s_attack": 0, "s_defense": 0, "accuracy": 0, "evasion": 0,
                          "speed": 0}

        # battlefield conditions
        self.weather = ["clear", 0]
        self.terrain = ["none", 0]
        self.p1_screens = {"reflect": 0, "light screen": 0}
        self.p2_screens = {"reflect": 0, "light screen": 0}

    def choose_pokemon_from_team(self, player, hp_check = False):
        if player == 1:
            trainer = self.trainer_1
            team = self.p1_team
        else:
            trainer = self.trainer_2
            team = self.p2_team
        print("Trainer: {}".format(trainer.name))
        while True:
            count = 1
            for pokemon in team:
                print(str(count) + ": " +
                      printer_outer(
                          printer_outer("Nickname: {}".format(pokemon.nickname), "Species: {}".format(pokemon.name),
                                        30),
                          printer_outer("HP: {}".format(pokemon.health), "Held Item: {}".format(pokemon.held_item),
                                        15), 55)
                      + "\n" + printer_outer("Stats: {}".format(list(pokemon.pokemon_stats.values())),
                                             "Moves: {}".format(pokemon.moveset), 40) + "\n"
                      )
                count += 1
            chosen_pokemon = input(
                "Which pokemon would you like to add to the team?(1 - {}, [enter] to stop)".format(len(team)))
            try:
                print("-" * 100)
                chosen_pokemon = int(chosen_pokemon) - 1
                print("Name: {},          Nickname: {}".format(team[chosen_pokemon].name,team[chosen_pokemon].nickname))
                if team[chosen_pokemon].health <= 0 and hp_check:
                    print("Pokemon hp below 0!")
                else:
                    return team[chosen_pokemon]
            except:
                print("Enter a number value!\n")

    def choose_pokemon(self, player):
        while True:
            if player == 1:
                pokemon = self.choose_pokemon_from_team(1)
                if pokemon.health > 0:
                    self.pokemon_1 = pokemon
                    break
                else:
                    print("Pokemon health below 0!")
            elif player == 2:
                pokemon = self.choose_pokemon_from_team(2)
                if pokemon.health > 0:
                    self.pokemon_2 = pokemon
                    break
                else:
                    print("Pokemon health below 0!")
        return pokemon

    def initialize_teams(self, num_pkmn):
        self.choose_team(num_pkmn)
        self.pokemon_1 = self.p1_team[0]
        self.pokemon_2 = self.p2_team[0]

    def printer_outer(self, message_1, message_2, chars):
        return message_1 + " " * (chars - len(message_1)) + message_2

    # for calculating power of a move

    def bst_calc(self, move, attacking_player):
        def bast_calc(c_type, p1_atk=1, p2_def=1, p1_satk=1, p2_sdef=1):
            if c_type == "physical":
                return p1_atk / p2_def
            elif c_type == "special":
                return p1_satk / p2_sdef
            else:
                print("C_type error in bst_calc")
                return 1

        if attacking_player == 1:
            return bast_calc(move["c_type"], self.pokemon_1.pokemon_stats["attack"],
                             self.pokemon_2.pokemon_stats["defense"], self.pokemon_1.pokemon_stats["s_attack"],
                             self.pokemon_2.pokemon_stats["s_defense"])
        elif attacking_player == 2:
            return bast_calc(move["c_type"], self.pokemon_2.pokemon_stats["attack"],
                             self.pokemon_1.pokemon_stats["defense"], self.pokemon_2.pokemon_stats["s_attack"],
                             self.pokemon_1.pokemon_stats["s_defense"])

    def accuracy_check(self, move_acc):
        token = random.randint(1, 101)
        acc_mult = move_acc
        if self.p1_boosts["accuracy"] > 0:
            acc_mult *= (3 + self.p1_boosts["accuracy"]) / 3
        else:
            acc_mult *= 3 / (3 - self.p1_boosts["accuracy"])
        if self.p2_boosts["evasion"] > 0:
            acc_mult /= (3 + self.p2_boosts["evasion"]) / 3
        else:
            acc_mult /= 3 / (3 - self.p2_boosts["evasion"])
        if acc_mult >= token:
            return True
        else:
            return False

    def c_mult(self, c_type, player):
        if player == 0:
            atk_mult = 1
            if player > 0:
                atk_mult *= (2 + player) / 2
            else:
                atk_mult *= 2 / (2 - player)
            return atk_mult
        if player == 1:
            if c_type == "physical":
                p1_atk = self.p1_boosts["attack"]
                p2_def = self.p2_boosts["defense"]
            else:
                p1_atk = self.p1_boosts["s_attack"]
                p2_def = self.p2_boosts["s_defense"]
        else:
            if c_type == "physical":
                p1_atk = self.p2_boosts["attack"]
                p2_def = self.p1_boosts["defense"]
            else:
                p1_atk = self.p2_boosts["s_attack"]
                p2_def = self.p1_boosts["s_defense"]
        atk_mult = 1
        if p1_atk > 0:
            atk_mult *= (2 + p1_atk) / 2
        else:
            atk_mult *= 2 / (2 - p1_atk)
        if p2_def > 0:
            atk_mult /= (2 + p2_def) / 2
        else:
            atk_mult /= 2 / (2 - p2_def)
        return atk_mult

    def speed_check(self, p1_priority=0, p2_priority=0, paralyzed=(False, False)):
        if p1_priority != 0 or p2_priority != 0:
            if p1_priority > p2_priority:
                return True
            elif p1_priority < p2_priority:
                return False
        if "paralyzed" in self.pokemon_1.status_condition:
            speed1_mult = 0.5
        else:
            speed1_mult = 1
        if "paralyzed" in self.pokemon_2.status_condition:
            speed2_mult = 0.5
        else:
            speed2_mult = 1
        if (self.pokemon_1.pokemon_stats["speed"] * self.c_mult(self.p1_boosts["speed"], 0)) > (
                self.pokemon_2.pokemon_stats["speed"] * self.c_mult(self.p2_boosts["speed"], 0)):
            # if terrain_conds["trick room"] > 0:
            # return False
            return True
        elif (self.pokemon_1.pokemon_stats["speed"] * self.c_mult(self.p1_boosts["speed"], 0)) < (
                self.pokemon_2.pokemon_stats["speed"] * self.c_mult(self.p2_boosts["speed"], 0)):
            # if terrain_conds["trick room"] > 0:
            # return True
            return False
        else:
            token = random.randint(0, 1)
            if token == 1:
                return False
            else:
                return True

    def weather_mult(self, move):
        if self.weather[0] == "rain":
            if move["type"] == "water":
                return 1.5
            elif move["type"] == "fire" or move["name"] == "solar beam" or move["name"] == "solar blade":
                return 0.5
        elif self.weather[0] == "sunny":
            if move["type"] == "fire":
                return 1.5
            elif move["type"] == "water":
                return 0.5
        elif self.weather[0] == "sandstorm":
            if move["name"] == "solar beam" or move["name"] == "solar blade":
                return 0.5
        elif self.weather[0] == "hail":
            if move["name"] == "solar beam" or move["name"] == "solar blade":
                return 0.5
        elif self.weather[0] == "extreme sun":
            if move["type"] == "fire":
                return 2
            elif move["type"] == "water":
                return 0
        elif self.weather[0] == "extreme rain":
            if move["type"] == "fire":
                return 0
            elif move["type"] == "water":
                return 2
        elif self.weather[0] == "delta stream":
            if move["type"] in ["rock", "ice", "electric"]:
                return 0.5
        return 1

    #####################################

    def move_calc(self, move_information, attacking_player):
        # setting attacking & defending pokemon & boosts
        if attacking_player == 1:
            atk_pokemon = self.pokemon_1
            def_pokemon = self.pokemon_2
            atk_stat_boost = self.p1_boosts
            def_stat_boost = self.p2_boosts
        else:
            atk_pokemon = self.pokemon_2
            def_pokemon = self.pokemon_1
            atk_stat_boost = self.p2_boosts
            def_stat_boost = self.p1_boosts

        move = move_information.copy()
        if "paralyzed" in self.pokemon_1.status_condition and random.randint(0, 4) == 4:
            return "paralyzed"
        elif "frozen" in self.pokemon_1.status_condition:
            return "frozen"
        elif "asleep" in self.pokemon_1.status_condition:
            return "asleep"
        elif "confused" in self.pokemon_1.status_condition and random.randint(0, 4) == 4:
            return "confused"

        hit_or_miss = self.accuracy_check(move_information["accuracy"])
        # special cases for accuracy
        if (move["name"] == "thunder" and self.weather[0] == "rain") or (
                move["name"] == "blizzard" and self.weather[0] == "hail"):
            hit_or_miss = True
        elif move["name"] in []:
            hit_or_miss = True

        if hit_or_miss == False:
            return "miss"

        self.set_weather(move["name"])
        self.set_weather(move["name"])
        self.set_screen(move["name"], attacking_player)

        if move["c_type"] == "status":
            return 0

        # basic move power modifiers
        type_mult = check_type(move["type"], def_pokemon.type)
        if type_mult == 0:
            return "immune"
        weather_mult = self.weather_mult(move_information)
        apparant_mult = self.bst_calc(move_information, attacking_player)
        if move["c_type"] == "physical":
            if "burn" in atk_pokemon.status_condition:
                c_multiply = self.c_mult(atk_stat_boost["attack"], def_stat_boost["defense"]) / 2
            else:
                c_multiply = self.c_mult(atk_stat_boost["attack"], def_stat_boost["defense"])
        elif move["c_type"] == "special":
            c_multiply = self.c_mult(atk_stat_boost["s_attack"], def_stat_boost["s_defense"])
        else:
            c_multiply = 1

        token = random.randint(0, 24)
        if token == 0:
            critical = 1.5 * 1 / c_multiply
            print("It's a critical hit!")
        else:
            critical = 1

        rand_token = (random.randint(86, 101)) / 100
        if move_information["type"] in atk_pokemon.type:
            STAB = 1.5
        else:
            STAB = 1

        other = 1
        # checking for held items
        if (def_pokemon.held_item == "soul dew" and def_pokemon.name == "latios") or (
                def_pokemon.held_item == "soul dew" and def_pokemon.name == "latias"):
            other *= 2 / 3
        if atk_pokemon.held_item == "life orb":
            other *= 1.3
        if atk_pokemon.held_item == "expert belt" and type_mult > 1:
            other *= 1.2
        if (def_pokemon.held_item == "eviolite") and (
                def_pokemon.name in ['pikachu', 'magneton', 'chansey', 'piloswine', 'bulbasaur', 'ivysaur',
                                     'charmander', 'charmeleon', 'squirtle', 'wartortle', 'weedle', 'kakuna', 'pidgey',
                                     'pidgeotto', 'zubat', 'golbat', 'meowth', 'poliwag', 'poliwhirl', 'abra',
                                     'kadabra', 'machop', 'machoke', 'bellsprout', 'weepinbell', 'geodude', 'graveler',
                                     'magnemite', 'ghastly', 'haunter', 'onix', 'exeggcute', 'horsea', 'seadra',
                                     'scyther', 'magikarp', 'eevee', 'dratini', 'dragonair', 'chikorita', 'bayleef',
                                     'cyndaquil', 'quilava', 'totodile', 'croconaw', 'togepi', 'togetic', 'mareep',
                                     'flaaffy', 'larvitar', 'pupitar', 'swinub', 'sneasel', 'treecko', 'grovyle',
                                     'torchic', 'combusken', 'mudkip', 'marshtomp', 'poochyena', 'lotad', 'lombre',
                                     'seedot', 'nuzleaf', 'ralts', 'kirlia', 'aron', 'lairon', 'electrike', 'carvanha',
                                     'numel', 'trapinch', 'vibrava', 'swablu', 'spheal', 'sealeo', 'bagon', 'shelgon',
                                     'beldum', 'metang', 'riolu', 'croagunk']):
            other *= 2 / 3

        # checking for terrain
        if (self.terrain[0] == "electric terrain") and (move["type"] == "electric"):
            other *= 1.5
        elif (self.terrain[0] == "grassy terrain") and (move["type"] == "grassy"):
            other *= 1.5
        elif (self.terrain[0] == "psychic terrain") and (move["type"] == "psychic"):
            other *= 1.5
        elif (self.terrain[0] == "misty terrain") and (move["type"] == "fairy"):
            other *= 1.5

        # checking for screens
        if attacking_player == 1:
            if self.p2_screens["reflect"] > 0:
                if move_information["c_type"] == "physical":
                    other *= 0.5
            if self.p2_screens["light screen"] > 0:
                if move_information["c_type"] == "special":
                    other *= 0.5
        if attacking_player == 2:
            if self.p1_screens["reflect"] > 0:
                if move_information["c_type"] == "physical":
                    other *= 0.5
            if self.p1_screens["light screen"] > 0:
                if move_information["c_type"] == "special":
                    other *= 0.5

        apparant_power = (((((2 * atk_pokemon.level) / 5) + 2) * move_information[
            "power"] * apparant_mult / 50) + 2) * type_mult * critical * rand_token * c_multiply * STAB * weather_mult * other
        return int(apparant_power)

    # dealing with stat boosts
    def boost_stat(self, stat, amnt, player):
        if player == 1:
            self.p1_boosts[stat] += amnt
            if self.p1_boosts[stat] > 6:
                self.p1_boosts[stat] = 6
            elif self.p1_boosts[stat] < -6:
                self.p1_boosts[stat] = -6
        if player == 2:
            self.p2_boosts[stat] += amnt
            if self.p2_boosts[stat] > 6:
                self.p2_boosts[stat] = 6
            elif self.p2_boosts[stat] < -6:
                self.p2_boosts[stat] = -6

    def boost_check(self, boosted, player):
        if player == 1:
            for stat in boosted.keys():
                for p1_stat in self.p1_boosts:
                    if stat == p1_stat:
                        self.boost_stat(stat, boosted[stat], player)
                for p2_stat in self.p2_boosts:
                    if stat[0] == "O" and stat[1:] == p2_stat:
                        self.boost_stat(stat[0:], -1 * boosted[stat], 2)
        elif player == 2:
            for stat in boosted.keys():
                for p2_stat in self.p2_boosts:
                    if stat == p2_stat:
                        self.boost_stat(stat, boosted[stat], player)
                for p1_stat in self.p1_boosts:
                    if stat[0] == "O" and stat[1:] == p1_stat:
                        self.boost_stat(stat[0:], -1 * boosted[stat], 1)

    def full_boost(self, move):
        if move["name"] == "ancient power":
            if random.randint(0, 9) == 0:
                return {"attack": 1, "defense": 1, "s_attack": 1, "s_defense": 1, "accuracy": 1, "evasion": 1,
                        "speed": 1}
            else:
                return {}
        else:
            boosts = {}
            for item in move["stat change"]:
                if type(move["stat change"][item]) != int:
                    token = random.randint(1, 101)
                    if token < (move["stat change"][item]) * 100:
                        boosts[item] = 1
                else:
                    boosts[item] = 1
            return boosts

    # battle conditions
    def weather_counter(self):
        if "clear" in self.weather:
            self.weather[1] = 0
        elif self.weather[0] in ["rainy", "sunny", "sandstorm", "hail"]:
            self.weather[1] -= 1
        if self.weather[1] < 1:
            self.weather[0] = "clear"
        return self.weather

    def terrain_counter(self):
        if "none" in self.terrain:
            self.terrain[1] = 0
        elif self.terrain[0] in ["grassy", "psychic", "electric", "misty"]:
            self.terrain[1] -= 1
        if self.terrain[1] < 1:
            self.terrain[0] = "none"
        return self.terrain

    def screen_counter(self):
        for item in self.p1_screens:
            self.p1_screens[item] -= 1
        for item in self.p2_screens:
            self.p2_screens[item] -= 1

    def set_weather(self, move):
        weather_dict = {"rain": ["rain dance"], "sunny": ["sunny day"], "sandstorm": ["sandstorm"], "hail": ["hail"]}
        for item in weather_dict:
            if move in weather_dict[item]:
                self.weather[0] = item
                self.weather[1] = 5
        return self.weather

    def set_terrain(self, move):
        terrain_dict = {"grassy": ["grassy terrain"], "psychic": ["psychic terrain"], "electric": ["electric terrain"],
                        "misty": ["misty terrain"]}
        for item in terrain_dict:
            if move in terrain_dict[item]:
                self.terrain[0] = item
                self.terrain[1] = 5
        return self.terrain

    def set_screen(self, move, player):
        screens = {"reflect": [], "light screen": []}
        for item in screens:
            if move in screens[item]:
                if player == 1:
                    self.p1_screens[item] = 5
                elif player == 2:
                    self.p2_screens[item] = 5
                else:
                    print("Error setting screen")

    # for displaying info
    def return_message(self, type_mul, move, pkmn_name):
        if type_mul == 0:
            return "The " + pkmn_name.title() + "'s " + move + " had no effect!"
        elif type_mul == 1 / 4:
            return "The " + pkmn_name.title() + "'s " + move + " was really not very effective!"
        elif type_mul == 1 / 2:
            return "The " + pkmn_name.title() + "'s " + move + " was not very effective!"
        elif type_mul == 1:
            return "The " + pkmn_name.title() + "'s " + move + " hit!"
        elif type_mul == 2:
            return ("The " + pkmn_name.title() + "'s " + move + " was super effective!")
        elif type_mul == 4:
            return ("The " + pkmn_name.title() + "'s " + move + " was really super effective")

    def display_items(self, player):
        if player == 1:
            print(self.p1_bag)
        elif player == 2:
            print(self.p2_bag)

    def clean_bag(self):
        def clean(item_bag):
            for key in list(item_bag.keys()).copy():
                if item_bag[key] == 0:
                    del item_bag[key]
            return item_bag

        self.p1_bag.bag = clean(self.p1_bag.bag)
        self.p2_bag.bag = clean(self.p2_bag.bag)

    def weather_check(self):
        if self.weather[0] == "sandstorm":
            if "rock" not in self.pokemon_1.type and "ground" not in self.pokemon_1.type and "steel" not in self.pokemon_1.type:
                self.p1_health -= self.pokemon_1.pokemon_stats["hp"] // 16
            if "rock" not in self.pokemon_2.type and "ground" not in self.pokemon_2.type and "steel" not in self.pokemon_2.type:
                self.p1_health -= self.pokemon_2.pokemon_stats["hp"] // 16
        elif self.weather[0] == "hail":
            if "ice" not in self.pokemon_1.type:
                self.p1_health -= self.pokemon_1.pokemon_stats["hp"] // 16
            if "ice" not in self.pokemon_2.type:
                self.p2_health -= self.pokemon_2.pokemon_stats["hp"] // 16

    def burn_poison(self, pokemon):
        if "poisoned" in pokemon.status_condition:
            pokemon.health -= pokemon.pokemon_stats["hp"] // 16
        if "burn" in pokemon.status_condition:
            if "fire" not in pokemon.type:
                pokemon.health -= pokemon.pokemon_stats["hp"] // 16
        if "badly poisoned" in pokemon.status_condition:
            pokemon.health -= pokemon.pokemon_stats // 8


    # held items
    def damage_from_items(self):
        if self.pokemon_1.held_item == "life orb":
            self.pokemon_1.health -= self.pokemon_1.pokemon_stats["hp"] // 10
        elif self.pokemon_1.held_item == "leftovers":
            self.pokemon_1.health += self.pokemon_1.pokemon_stats["hp"] // 10
        if self.pokemon_2.held_item == "life orb":
            self.pokemon_2.health -= self.pokemon_2.pokemon_stats["hp"] // 10
        elif self.pokemon_2.held_item == "leftovers":
            self.pokemon_2.health += self.pokemon_2.pokemon_stats["hp"] // 10


    def get_move(self, player):
        if player == 1:
            pokemon = self.pokemon_1
            item_bag = self.trainer_1.bag
            trainer = self.trainer_1
        else:
            pokemon = self.pokemon_2
            item_bag = self.trainer_2.bag
            trainer = self.trainer_2
        print("-" * 100)
        print("{}: ".format(trainer.name))
        print("Attacks:")
        print(pokemon.print_moveset())
        print("-" * 100)
        print(item_bag.print_battle_items())
        while True:
            print("-" * 100)
            move = (input("Select move: ")).lower()
            if move in pokemon.moveset or move == "switch":
                break
            if move in item_bag.bag.keys():
                if "ball" in move:
                    break
                if move not in battle_items:
                    print("Not an item to be used in battle!")
                if item_bag.bag[move] < 1:
                    print("Not enough of item!")
            print("Not a valid move!\n")
        return move


    def choose_team(self, num_pokemon):
        self.p1_team = []
        self.p2_team = []
        for i in range (num_pokemon):
            print("Player 1:")
            self.p1_team.append(self.trainer_1.choose_pokemon())
            print("Player 2:")
            self.p2_team.append(self.trainer_2.choose_pokemon())
        return self.p1_team, self.p2_team

    def __repr__(self):
        return_string = "-" * 150 + "\n"
        num_bars_1 = int(self.pokemon_1.health / self.pokemon_1.pokemon_stats["hp"] * 30)
        num_bars_2 = int(self.pokemon_2.health / self.pokemon_2.pokemon_stats["hp"] * 30)
        healthbar_1 = "=" * num_bars_1 + "_" * (30 - num_bars_1)
        healthbar_2 = "=" * num_bars_2 + "_" * (30 - num_bars_2)

        return_string += printer_outer("Trainer 1: " + self.trainer_1.name, "Trainer 2: " + self.trainer_2.name, 80) + "\n"
        return_string += printer_outer(printer_outer("Pokemon 1: {}".format(self.pokemon_1.name.title()), "Lvl: {}".format(self.pokemon_1.level), 30),
                            printer_outer("Pokemon 2: {}".format(self.pokemon_2.name.title()), "Lvl: {}".format(self.pokemon_2.level), 30), 80) + "\n"
        return_string += printer_outer(printer_outer("HP: " + str(self.pokemon_1.health) + "/" + str(self.pokemon_1.pokemon_stats["hp"]), "Status: {}".format(self.pokemon_1.status_condition), 30),
                            printer_outer("HP: " + str(self.pokemon_2.health) + "/" + str(self.pokemon_2.pokemon_stats["hp"]), "Status: {}".format(self.pokemon_2.status_condition), 30), 80) + "\n"
        return_string += printer_outer(healthbar_1, healthbar_2, 80) + "\n"

        return_string += "-" * 150 + "\n"
        return_string += "{} Moves: {}\n{} Moves: {}".format(self.trainer_1.name, self.pokemon_1.moveset, self.trainer_2.name, self.pokemon_2.moveset)
        return (return_string)


class Bag:
    def __init__(self, bag={}, money=0):
        self.bag = bag
        self.money = money

    def add_to_bag(self, item, amnt=1):
        if item not in self.bag:
            self.bag[item] = 0
        self.bag[item] += amnt

    def remove_from_bag(self, item, amnt=1):
        if item not in self.bag:
            return False
        self.bag[item] -= amnt
        if self.bag[item] < 0:
            self.bag[item] += amnt
            return False
        return True

    def remove_money(self, amnt=0):
        if self.money < amnt:
            return False
        else:
            self.money -= amnt
            return True

    def add_money(self, amnt=0):
        self.money += amnt

    def buy(self, item, amnt=0, unit_cost=0):
        if self.remove_money(unit_cost * amnt) == False:
            return False
        else:
            self.add_to_bag(item, amnt)
            return True

    def print_battle_items(self):
        clean_bag = {}
        for item in self.bag:
            if self.bag[item] > 0 and item in battle_items:
                clean_bag[item] = self.bag[item]
        return "Battle Items: {}".format(clean_bag)

    def buying(self):
        print("item", "price", "Description")
        for item in items.keys():
            print(items[item]["item"], items[item]["price"])
        while True:
            print("\n")
            print("Money: " + str(self.money))
            print("Which item would you like to buy?(Type D if you are done) ")
            bought = input("Item bought: ")
            if bought.lower() == "d":
                break
            if bought not in items.keys():
                print("Not a valid item!")
            else:
                try:
                    amount = int(input("How many would you like to buy?"))
                    check_bought = self.buy(bought, amount, items[bought]["price"])
                    if check_bought == False:
                        print("Not enough money")
                    else:
                        print("You bought {} number of the item {}, costing you {} each".format(amount, bought,
                                                                                                items[bought]["price"]))
                except:
                    print("Enter a number value")
            if self.money <= 0:
                break

    def __repr__(self):
        clean_bag = {}
        for item in self.bag:
            if self.bag[item] > 0:
                clean_bag[item] = self.bag[item]
        return "Bag: {}".format(clean_bag)



#battle = Battle()
#battle.p1_bag.add_to_bag("potion", 5)
#battle.p1_bag.add_to_bag("hyper potion", 2)
#battle.p1_bag.buying()
#print(battle.trainer_1.encoder("trainer_info"))


def gen_rand(tier):
    pokedex = pokedex_decoder()
    if tier != 0:
        def gen_rand_name(tier):
            tiers = {
                "T0": ["bulbasaur", "charmander", "squirtle"],
                "T1": ["pikachu", "pidgey", "weedle", "zubat"],
                "T2": ["bellsprout", "geodude", "machop", "magikarp", "poliwag"],
                "T3": ["abra", "ghastly", "chansey", "pinsir", "exeggutor", "meowth", "magnemite", "eevee"],
                "T4": ["aerodactyl", "lapras", "snorlax", "scyther", "horsea", "dratini", "onix", "golbat", "kakuna"],
                "T5": ["haunter", "kadabra", "graveler", "machoke", "seadra", "raichu", "pidgeot", "dragonair"],
                "T6": ["flareon", "vaporeon", "jolteon", "magneton", "persian", "beedrill"],
                "T7": ["ivysaur", "charmeleon", "wartortle", "weepinbell", "pinsir", "exeggutor"],
                "T8": ["golem", "machamp", "victreebel", "gengar", "alakazam", "poliwrath", "raichu"],
                "T9": ["venusaur", "charizard", "blastoise", "gyarados", "dragonite"],
                "T10": ["articuno", "moltres", "zapdos", "mewtwo", "mew"]
            }
            poke_pool = []
            for i in range(1, tier + 1):
                poke_pool += tiers["T" + str(i)] * (tier - i + 1)
            return random.choice(poke_pool)
        name = gen_rand_name(tier)
    else:
        name = random.choice(["charmander", "bulbasaur", "squirtle"])
    return Pokemon(name, pokedex[name]["moves"], pokedex[name]["ability"], [], "", tier * 5, 0, [0, 0, 0, 0, 0, 0], [random.randint(1,32), random.randint(1,32), random.randint(1,32), random.randint(1,32), random.randint(1,32), random.randint(1,32)],
                   random.choice(
                       ["hardy", "lonely", "adament", "naughty", "brave", "bold", "docile", "impish", "lax", "relaxed",
                        "modest", "mild", "bashful", "rash", "quiet", "calm", "gentle", "careful", "quirky", "sassy",
                        "timid", "hasty", "jolly", "naive", "serious"])
                   , name, 0, "pokeball")
