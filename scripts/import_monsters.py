# scripts/import_monsters.py
"""
Script to import monster data from Excel spreadsheet to JSON format.
"""
import pandas as pd
import json
import os
import sys
from pathlib import Path

def import_monsters_from_excel(excel_file_path, output_json_path=None):
    """
    Import monster data from Excel file and convert to JSON format.
    
    Args:
        excel_file_path: Path to the Excel file
        output_json_path: Path for output JSON (optional)
    """
    
    if output_json_path is None:
        # Default to data/monsters.json
        script_dir = Path(__file__).parent
        project_dir = script_dir.parent
        output_json_path = project_dir / 'data' / 'monsters.json'
    
    try:
        print(f"Reading Excel file: {excel_file_path}")
        
        # Read the Excel file
        excel_data = pd.ExcelFile(excel_file_path)
        
        # Initialize the data structure
        monster_data = {
            "monsters": {},
            "encounter_tables": {},
            "subtables": {}
        }
        
        # Import monsters sheet
        if 'Monsters' in excel_data.sheet_names:
            print("Importing monsters...")
            monsters_df = pd.read_excel(excel_file_path, sheet_name='Monsters')
            monster_data["monsters"] = import_monsters_sheet(monsters_df)
            print(f"Imported {len(monster_data['monsters'])} monsters")
        
        # Import encounter tables sheet
        if 'Encounter Tables' in excel_data.sheet_names:
            print("Importing encounter tables...")
            encounter_df = pd.read_excel(excel_file_path, sheet_name='Encounter Tables')
            monster_data["encounter_tables"] = import_encounter_tables_sheet(encounter_df)
            print(f"Imported {len(monster_data['encounter_tables'])} encounter tables")
        
        # Import subtables sheet
        if 'Subtables' in excel_data.sheet_names:
            print("Importing subtables...")
            subtables_df = pd.read_excel(excel_file_path, sheet_name='Subtables')
            monster_data["subtables"] = import_subtables_sheet(subtables_df)
            print(f"Imported {len(monster_data['subtables'])} subtables")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        
        # Write JSON file
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(monster_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully exported to: {output_json_path}")
        
        # Validate the exported data
        validate_monster_data(monster_data)
        
        return True
        
    except Exception as e:
        print(f"Error importing monsters: {e}")
        import traceback
        traceback.print_exc()
        return False

def import_monsters_sheet(df):
    """Import the monsters sheet from DataFrame."""
    monsters = {}
    
    for _, row in df.iterrows():
        try:
            # Skip empty rows
            if pd.isna(row.get('monster_id')):
                continue
            
            monster_id = str(row['monster_id']).strip()
            
            # Build attacks list
            attacks = []
            for i in range(1, 4):  # Up to 3 attacks
                attack_name = row.get(f'attack{i}_name')
                attack_damage = row.get(f'attack{i}_damage') 
                attack_type = row.get(f'attack{i}_type')
                
                if pd.notna(attack_name) and attack_name.strip():
                    attacks.append({
                        "name": str(attack_name).strip(),
                        "damage": str(attack_damage).strip() if pd.notna(attack_damage) else "1d6",
                        "type": str(attack_type).strip() if pd.notna(attack_type) else "melee"
                    })
            
            # Default attack if none specified
            if not attacks:
                attacks = [{"name": "weapon", "damage": "1d6", "type": "melee"}]
            
            # Parse special abilities
            special_abilities = []
            abilities_str = row.get('special_abilities')
            if pd.notna(abilities_str) and str(abilities_str).strip():
                special_abilities = [s.strip() for s in str(abilities_str).split(',')]
            
            # Build monster data
            monster = {
                "name": str(row['name']).strip(),
                "char": str(row['char']).strip(),
                "color": [
                    int(row.get('color_r', 100)),
                    int(row.get('color_g', 100)), 
                    int(row.get('color_b', 100))
                ],
                "ac": int(row.get('ac', 10)),
                "hd": float(row.get('hd', 1)),
                "hp_roll": str(row.get('hp_roll', '1d8')).strip(),
                "attacks": attacks,
                "thac0": int(row.get('thac0', 19)),
                "movement": int(row.get('movement', 120)),
                "saves": {
                    "death": int(row.get('save_death', 14)),
                    "wands": int(row.get('save_wands', 15)),
                    "paralysis": int(row.get('save_paralysis', 16)),
                    "breath": int(row.get('save_breath', 17)),
                    "spells": int(row.get('save_spells', 18))
                },
                "morale": int(row.get('morale', 8)),
                "alignment": str(row.get('alignment', 'Neutral')).strip(),
                "xp_value": int(row.get('xp_value', 10)),
                "special_abilities": special_abilities,
                "encounter_size": str(row.get('encounter_size', '1')).strip()
            }
            
            monsters[monster_id] = monster
            
        except Exception as e:
            print(f"Error processing monster row {row.get('monster_id', 'unknown')}: {e}")
            continue
    
    return monsters

def import_encounter_tables_sheet(df):
    """Import the encounter tables sheet from DataFrame."""
    encounter_tables = {}
    
    for _, row in df.iterrows():
        try:
            terrain = str(row['terrain']).strip()
            if pd.isna(terrain):
                continue
            
            table = {}
            for i in range(1, 9):  # d8 rolls
                roll_col = f'roll_{i}'
                if roll_col in row and pd.notna(row[roll_col]):
                    entry_str = str(row[roll_col]).strip()
                    
                    if ':' in entry_str:
                        # Format: "category:subtable" or "direct:monster_id"
                        category, target = entry_str.split(':', 1)
                        if category == 'direct':
                            table[str(i)] = {"result": target}
                        else:
                            table[str(i)] = {"category": category, "subtable": target}
                    else:
                        # Direct monster reference
                        table[str(i)] = {"result": entry_str}
            
            if table:
                encounter_tables[terrain] = table
                
        except Exception as e:
            print(f"Error processing encounter table row {row.get('terrain', 'unknown')}: {e}")
            continue
    
    return encounter_tables

def import_subtables_sheet(df):
    """Import the subtables sheet from DataFrame."""
    subtables = {}
    
    for _, row in df.iterrows():
        try:
            subtable_name = str(row['subtable_name']).strip()
            if pd.isna(subtable_name):
                continue
            
            subtable = {}
            
            # Process range columns
            for col in df.columns:
                if col.startswith('range_'):
                    if pd.notna(row[col]) and str(row[col]).strip():
                        # Extract range from column name (e.g., 'range_1_3' -> '1-3')
                        range_part = col.replace('range_', '').replace('_', '-')
                        monster_id = str(row[col]).strip()
                        subtable[range_part] = monster_id
            
            if subtable:
                subtables[subtable_name] = subtable
                
        except Exception as e:
            print(f"Error processing subtable row {row.get('subtable_name', 'unknown')}: {e}")
            continue
    
    return subtables

def validate_monster_data(data):
    """Validate the imported monster data."""
    print("\nValidating imported data...")
    
    errors = []
    
    # Check for required fields in monsters
    for monster_id, monster in data["monsters"].items():
        required_fields = ['name', 'char', 'color', 'ac', 'hd', 'hp_roll', 'attacks', 'thac0']
        for field in required_fields:
            if field not in monster:
                errors.append(f"Monster {monster_id} missing required field: {field}")
    
    # Check encounter table references
    for terrain, table in data["encounter_tables"].items():
        for roll, entry in table.items():
            if 'subtable' in entry:
                subtable_name = entry['subtable']
                if subtable_name not in data["subtables"]:
                    errors.append(f"Encounter table {terrain} references missing subtable: {subtable_name}")
            elif 'result' in entry:
                monster_id = entry['result']
                if monster_id not in data["monsters"]:
                    errors.append(f"Encounter table {terrain} references missing monster: {monster_id}")
    
    # Check subtable references
    for subtable_name, subtable in data["subtables"].items():
        for range_key, monster_id in subtable.items():
            if monster_id not in data["monsters"]:
                errors.append(f"Subtable {subtable_name} references missing monster: {monster_id}")
    
    if errors:
        print(f"Found {len(errors)} validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ All validation checks passed!")

def create_sample_excel():
    """Create a sample Excel file with the correct format."""
    
    # Sample monster data
    monsters_data = [
        {
            'monster_id': 'kobold',
            'name': 'Kobold',
            'char': 'k',
            'color_r': 113, 'color_g': 65, 'color_b': 59,
            'ac': 7, 'hd': 0.5, 'hp_roll': '1d4+1', 'thac0': 19, 'movement': 60,
            'morale': 6, 'alignment': 'Chaotic', 'xp_value': 5, 'encounter_size': '4d4',
            'attack1_name': 'weapon', 'attack1_damage': '1d4-1', 'attack1_type': 'melee',
            'attack2_name': '', 'attack2_damage': '', 'attack2_type': '',
            'attack3_name': '', 'attack3_damage': '', 'attack3_type': '',
            'save_death': 14, 'save_wands': 15, 'save_paralysis': 16, 'save_breath': 17, 'save_spells': 18,
            'special_abilities': 'ambush,infravision_90,hate_gnomes'
        },
        {
            'monster_id': 'goblin',
            'name': 'Goblin',
            'char': 'g',
            'color_r': 139, 'color_g': 69, 'color_b': 19,
            'ac': 6, 'hd': 1, 'hp_roll': '1d8', 'thac0': 19, 'movement': 60,
            'morale': 7, 'alignment': 'Chaotic', 'xp_value': 10, 'encounter_size': '2d4',
            'attack1_name': 'weapon', 'attack1_damage': '1d6', 'attack1_type': 'melee',
            'attack2_name': '', 'attack2_damage': '', 'attack2_type': '',
            'attack3_name': '', 'attack3_damage': '', 'attack3_type': '',
            'save_death': 14, 'save_wands': 15, 'save_paralysis': 16, 'save_breath': 17, 'save_spells': 18,
            'special_abilities': 'infravision_60'
        }
    ]
    
    # Sample encounter tables
    encounter_data = [
        {
            'terrain': 'forest',
            'roll_1': 'animal:forest_animal',
            'roll_2': 'dragon:dragon_flyer_insect', 
            'roll_3': 'flyer:dragon_flyer_insect',
            'roll_4': 'human:forest_human',
            'roll_5': 'humanoid:forest_humanoid',
            'roll_6': 'insect:dragon_flyer_insect',
            'roll_7': 'monster:forest_monster',
            'roll_8': 'unusual:unusual'
        }
    ]
    
    # Sample subtables
    subtable_data = [
        {
            'subtable_name': 'forest_humanoid',
            'range_1_3': 'goblin',
            'range_4_6': 'kobold',
            'range_7_9': 'orc',
            'range_10_12': 'elf',
            'range_13_15': 'hobgoblin',
            'range_16_18': 'gnoll',
            'range_19_20': 'troll'
        }
    ]
    
    # Create Excel file
    output_file = 'monster_template.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        pd.DataFrame(monsters_data).to_excel(writer, sheet_name='Monsters', index=False)
        pd.DataFrame(encounter_data).to_excel(writer, sheet_name='Encounter Tables', index=False)
        pd.DataFrame(subtable_data).to_excel(writer, sheet_name='Subtables', index=False)
    
    print(f"Created sample Excel template: {output_file}")
    return output_file

def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python import_monsters.py <excel_file> [output_json]")
        print("   or: python import_monsters.py --create-sample")
        return
    
    if sys.argv[1] == '--create-sample':
        create_sample_excel()
        return
    
    excel_file = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found: {excel_file}")
        return
    
    success = import_monsters_from_excel(excel_file, output_json)
    if success:
        print("Import completed successfully!")
    else:
        print("Import failed!")

if __name__ == '__main__':
    main()