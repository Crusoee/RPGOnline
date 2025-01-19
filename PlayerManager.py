from Player import Player

class PlayerManager:
    def __init__(self, player):
        self.player = player
        self.all_players = {player.updates['nme'] : self.player}

    def update_all_players_list(self, shared_memory):
        for key, value in shared_memory['playersupdate'][0].items():
            if key not in self.all_players.keys():
                self.all_players[key] = Player(shared_memory['playersupdate'][0][key]['x'],shared_memory['playersupdate'][0][key]['y'],key)

        try:
            for name, player in self.all_players.items():
                player.stats = shared_memory['playersinfo'][0][name]
                if name in shared_memory['playersupdate'][0].keys() and name != self.player.updates['nme']:
                    player.updates = shared_memory['playersupdate'][0][name]
        except KeyError as e:
            self.all_players.pop(name)

    def move_players(self):
        for name, player in self.all_players.items():
            player.move()

    def sort_players(self):
        self.all_players = dict(sorted(self.all_players.items(), key=lambda item: item[1].updates['y']))
            
