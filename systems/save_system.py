# systems/save_system.py
"""
Save and load system for the ASCII RPG game.
"""
import json
import os
from datetime import datetime
from entities.player import Player
from entities.character import Character
from entities.items import Item
from world.world import World

class SaveSystem:
    """Handles saving and loading game data."""
    
    @staticmethod
    def save_game(player, world, slot=1):
        """Save game data to specified slot."""
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'character_name': player.character.name,
            'character_class': player.character.char_class,
            'level': player.character.level,
            'xp': player.character.xp,
            'hp': player.character.hp,
            'max_hp': player.character.max_hp,
            'ability_scores': player.character.ability_scores,
            'thac0': player.character.thac0,
            'saving_throws': player.character.saving_throws,
            'player_x': player.x,
            'player_y': player.y,
            'location': player.location,
            'overworld_pos': player.overworld_pos,
            
            # Inventory
            'inventory': [SaveSystem._serialize_item(item) for item in player.character.inventory],
            
            # Equipment
            'equipped': {
                slot: SaveSystem._serialize_item(item) if item else None 
                for slot, item in player.character.equipped.items()
            },
            
            # World data
            'world_seed': getattr(world, 'seed', None),  # If we implement world seeds
            'treasure_chests': [
                {
                    'pos': chest['pos'],
                    'item': SaveSystem._serialize_item(chest['item'])
                }
                for chest in world.treasure_chests
            ],
            
            # World state - save which tiles have been modified
            'world_modifications': getattr(world, 'modifications', {}),
            
            # Dungeon state
            'dungeon_rooms': len(world.rooms),
            'entrances': world.entrances
        }
        
        filename = f"save_slot_{slot}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    @staticmethod
    def load_game(slot=1):
        """Load game data from specified slot."""
        filename = f"save_slot_{slot}.json"
        
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            # Create character
            character = Character()
            character.name = save_data['character_name']
            character.char_class = save_data['character_class']
            character.level = save_data['level']
            character.xp = save_data['xp']
            character.hp = save_data['hp']
            character.max_hp = save_data['max_hp']
            character.ability_scores = save_data['ability_scores']
            character.thac0 = save_data['thac0']
            character.saving_throws = save_data['saving_throws']
            
            # Load inventory
            character.inventory = [
                SaveSystem._deserialize_item(item_data) 
                for item_data in save_data['inventory']
            ]
            
            # Load equipment
            character.equipped = {
                slot: SaveSystem._deserialize_item(item_data) if item_data else None
                for slot, item_data in save_data['equipped'].items()
            }
            
            # Create player
            player = Player(save_data['player_x'], save_data['player_y'])
            player.character = character
            player.location = save_data['location']
            player.overworld_pos = tuple(save_data['overworld_pos'])
            
            return {
                'player': player,
                'world_data': {
                    'treasure_chests': save_data.get('treasure_chests', []),
                    'seed': save_data.get('world_seed'),
                    'modifications': save_data.get('world_modifications', {}),
                    'entrances': save_data.get('entrances', [])
                }
            }
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    @staticmethod
    def _serialize_item(item):
        """Convert an Item object to a dictionary."""
        if item is None:
            return None
        
        return {
            'name': item.name,
            'char': item.char,
            'color': item.color,
            'slot': item.slot,
            'item_type': item.item_type,
            'hands': item.hands,
            'damage': item.damage,
            'defense': item.defense
        }
    
    @staticmethod
    def _deserialize_item(item_data):
        """Convert a dictionary back to an Item object."""
        if item_data is None:
            return None
        
        return Item(
            name=item_data['name'],
            char=item_data['char'],
            color=item_data['color'],
            slot=item_data['slot'],
            item_type=item_data['item_type'],
            hands=item_data['hands'],
            damage=item_data['damage'],
            defense=item_data['defense']
        )
    
    @staticmethod
    def delete_save(slot=1):
        """Delete a save file."""
        filename = f"save_slot_{slot}.json"
        try:
            if os.path.exists(filename):
                os.remove(filename)
                return True
        except Exception as e:
            print(f"Error deleting save: {e}")
        return False
    
    @staticmethod
    def save_exists(slot=1):
        """Check if a save file exists."""
        filename = f"save_slot_{slot}.json"
        return os.path.exists(filename)
    
    @staticmethod
    def get_save_info(slot=1):
        """Get basic info about a save file without fully loading it."""
        filename = f"save_slot_{slot}.json"
        
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            return {
                'character_name': save_data['character_name'],
                'character_class': save_data['character_class'],
                'level': save_data['level'],
                'location': save_data['location'],
                'timestamp': save_data['timestamp'],
                'hp': save_data['hp'],
                'max_hp': save_data['max_hp']
            }
        except Exception as e:
            print(f"Error reading save info: {e}")
            return None
    
    @staticmethod
    def get_all_saves():
        """Get info for all save slots."""
        saves = {}
        for slot in range(1, 4):  # Slots 1-3
            save_info = SaveSystem.get_save_info(slot)
            saves[slot] = save_info
        return saves
    
    @staticmethod
    def auto_save(player, world):
        """Auto-save to a special auto-save slot."""
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'character_name': player.character.name,
            'character_class': player.character.char_class,
            'level': player.character.level,
            'xp': player.character.xp,
            'hp': player.character.hp,
            'max_hp': player.character.max_hp,
            'ability_scores': player.character.ability_scores,
            'thac0': player.character.thac0,
            'saving_throws': player.character.saving_throws,
            'player_x': player.x,
            'player_y': player.y,
            'location': player.location,
            'overworld_pos': player.overworld_pos,
            
            # Inventory
            'inventory': [SaveSystem._serialize_item(item) for item in player.character.inventory],
            
            # Equipment
            'equipped': {
                slot: SaveSystem._serialize_item(item) if item else None 
                for slot, item in player.character.equipped.items()
            },
            
            # World data
            'world_seed': getattr(world, 'seed', None),
            'treasure_chests': [
                {
                    'pos': chest['pos'],
                    'item': SaveSystem._serialize_item(chest['item'])
                }
                for chest in world.treasure_chests
            ],
            'world_modifications': getattr(world, 'modifications', {}),
            'entrances': world.entrances
        }
        
        filename = "autosave.json"
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error auto-saving game: {e}")
            return False