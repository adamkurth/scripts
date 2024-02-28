from rcsbsearchapi.search import TextQuery, AttributeQuery, SequenceQuery, SeqMotifQuery, StructSimilarityQuery, Attr
from rcsbsearchapi import rcsb_attributes as attrs
from rcsbsearchapi.const import STRUCTURE_ATTRIBUTE_SEARCH_SERVICE
import argparse
# From rcsbsearchapi 
# comment and add as needed, for reference check the quickstart.ipynb in rcsbsearchapi repo 

def get_pdb_ids(space_group, str_type, limit=50):
    # By default, service is set to "text" for structural attribute search
    q1 = AttributeQuery("symmetry.cell_setting", "exact_match", str_type, STRUCTURE_ATTRIBUTE_SEARCH_SERVICE)
    q2 = AttributeQuery("symmetry.space_group_name_H_M", "exact_match", space_group, STRUCTURE_ATTRIBUTE_SEARCH_SERVICE)
    query = q2  # combining queries use & | operators
    pdb_ids = list(query())
    pdb_lim = truncate(pdb_ids, limit)
    print(f"From search: {space_group} \n", pdb_lim)
    return pdb_lim

def truncate(pdb_ids, limit):
    if len(pdb_ids) > limit:
        pdb_ids = pdb_ids[:limit]
    return pdb_ids


def interactive_script():
    parser = argparse.ArgumentParser(description='Download PDB files based on symmetry and space group.')
    parser.add_argument('symmetry_shape', type=str, help='Crystal symmetry to list space groups for')
    parser.add_argument('--limit', type=int, default=50, help='Limit number of PDB files to download (default: 50)')
    
    args, _ = parser.parse_known_args()
    
    symmetry_shape = args.symmetry_shape
    symmetry_shape = symmetry_shape.lower()
    limit = args.limit
        
    space_groups = {
        # Additional space groups from International Tables for Crystallography (ITC)
        "cubic": ["P 2 3", "F 2 3", "I 2 3", "P 21 3", "I 21 3", "P 4 3 2", "P 42 3 2", "F 4 3 2", "F 41 3 2", "I 4 3 2", "P 43 3 2", "P 41 3 2", "I 41 3 2", "P 42 3 2", "I 42 3 2", "F 43 3 2", "F 41 3 2", "I 43 3 2", "P 4 3 3", "F 4 3 3", "I 4 3 3", "P 41 3 3", "I 41 3 3", "P 42 3 3", "I 42 3 3", "P 43 3 3", "I 43 3 3"],
        "tetragonal": ["P 4 2 2", "P 42 2 2", "P 4 21 2", "P 41 2 2", "P 41 21 2", "P 42 21 2", "I 4 2 2", "I 41 2 2", "P 4 2 3", "P 42 2 3", "F 4 2 3", "F 41 2 3", "I 4 2 3", "P 43 2 3", "P 41 2 3", "I 41 2 3", "P 42 2 3", "I 42 2 3", "F 43 2 3", "F 41 2 3", "I 43 2 3"],
        "orthorhombic": ["P 2 2 2", "P 2 2 21", "P 2 21 2", "P 21 2 2", "P 21 2 21", "P 21 21 2", "P 21 21 21", "C 2 2 21", "C 2 2 2", "F 2 2 2", "I 2 2 2", "P 2 2 2 1", "P 2 2 21 1", "P 2 21 2 1", "P 21 2 2 1", "P 21 2 21 1", "P 21 21 2 1", "P 21 21 21 1", "C 2 2 21 1", "C 2 2 2 1", "F 2 2 2 1", "I 2 2 2 1"],
        "hexagonal": ["P 3", "P 31", "P 32", "P 3 1 2", "P 3 2 1", "R 3", "R 3 2", "P -3", "P 3*", "P 31*", "P 32*", "R 3*", "R 3 2*", "P -3*", "R -3", "R -3 2", "P 3 1 21", "P 3 21 1", "P 31 1 2", "P 31 2 1", "P 32 1 2", "P 32 2 1", "P 6", "P 61", "P 65", "P 62", "P 64", "P 63", "P 6 1 22", "P 6 5 22", "P 6 2 22", "P 6 4 22", "P 6 3 22", "P 6 1 2 1", "P 6 5 2 1", "P 6 2 2 1", "P 6 4 2 1", "P 6 3 2 1"],
        "trigonal": ["P 3", "P 31", "P 32", "P 3 1 2", "P 3 2 1", "R 3", "R 3 2", "P -3", "P 3*", "P 31*", "P 32*", "R 3*", "R 3 2*", "P -3*", "R -3", "R -3 2", "P 3 1 21", "P 3 21 1", "P 31 1 2", "P 31 2 1", "P 32 1 2", "P 32 2 1", "P 3 1 2 1", "P 3 2 1 1", "R 3 2 1", "P 3 1 21 1", "P 3 21 1 1", "P 31 1 2 1", "P 31 2 1 1", "P 32 1 2 1", "P 32 2 1 1", "P 3 1 2 1 1", "P 3 2 1 1 1", "R 3 2 1 1"],
        "monoclinic": ["P 2 1", "P 21", "C 2 2", "P 2 2 21", "P 2 21 2", "P 21 2 2", "P 21 21 2", "P 21 21 21", "C 2 2 21", "C 2 2 2", "I 2 2 2", "P 2 2 2 1", "P 2 2 21 1", "P 2 21 2 1", "P 21 2 2 1", "P 21 2 21 1", "P 21 21 2 1", "P 21 21 21 1", "C 2 2 21 1", "C 2 2 2 1", "I 2 2 2 1"],
        "triclinic": ["P 1", "P -1", "P 1 1 2", "P 1 1 21", "P 1 21 1", "P 21 1 1", "P 1 21 21", "P 21 1 21", "P 21 21 1", "P 1 1 2 1", "P 1 1 21 1", "P 1 21 1 1", "P 21 1 1 1", "P 1 21 21 1", "P 21 1 21 1", "P 21 21 1 1", "P 1 1 2 1 1", "P 1 1 21 1 1", "P 1 21 1 1 1", "P 21 1 1 1 1", "P 1 21 21 1 1", "P 21 1 21 1 1", "P 21 21 1 1 1"],
    }
    
    # Check if the symmetry_shape is valid and list possible space groups
    if symmetry_shape in space_groups:
        print(f"Select a space group for symmetry shape '{symmetry_shape}':")
        for idx, sg in enumerate(space_groups[symmetry_shape], 1):
            print(f"{idx}. {sg}")
        
        # Prompt the user to select a space group
        sg_choice = int(input("Enter the number of your chosen space group: "))
        if 1 <= sg_choice <= len(space_groups[symmetry_shape]):
            selected_space_group = space_groups[symmetry_shape][sg_choice - 1]
            print(f"You have selected space group '{selected_space_group}'.")
            print(f"Retrieving up to {limit} PDB IDs for space group '{selected_space_group}'...")
            
            # Retrieve and print PDB IDs for the selected space group
            ids = get_pdb_ids(selected_space_group, symmetry_shape, limit)
        else:
            print("Invalid choice. Please run the script again and select a valid number.")
    else:
        print(f"Invalid symmetry shape '{symmetry_shape}'. Please run the script again with a valid symmetry shape.")

if __name__ == "__main__":
    interactive_script()