import requests
import os
import argparse
from scrape import get_pdb_ids  # Import the function from scrape.py

class ProteinDownloader:
    """Class to download PDB files for specified proteins."""
    
    def __init__(self, base_dir=None):
        """Initialize ProteinDownloader class."""
        self.base_dir = base_dir or os.getcwd()

    def is_url_accessible(self, url):
        """Check if a URL is accessible."""
        response = requests.head(url)
        return response.status_code == 200

    def download_files(self, protein_ids, space_group):
        """Download PDB files for specified proteins, organized by space group."""
        formatted_space_group = space_group.replace(" ", "")  # remove spaces
        target_dir = os.path.join(self.base_dir, f"{formatted_space_group}/data/ids")
        os.makedirs(target_dir, exist_ok=True)  # Create directory structure
        
        PDB_URL_TEMPLATE = "https://files.rcsb.org/download/{}.pdb"
        
        for protein_id in protein_ids:
            print(f"Processing Protein: {protein_id}, Space Group: {formatted_space_group}")
            pdb_url = PDB_URL_TEMPLATE.format(protein_id)
            
            if self.is_url_accessible(pdb_url):
                response = requests.get(pdb_url)
                with open(os.path.join(target_dir, f"{protein_id}.pdb"), 'wb') as file:
                    file.write(response.content)
            else:
                print(f"URL not accessible for Protein ID: {protein_id}")
                
def main():
    parser = argparse.ArgumentParser(description='Download PDB files based on space group and symmetry.')
    parser.add_argument('symmetry_shape', type=str, help='Crystal symmetry to list space groups for')
    parser.add_argument('--limit', type=int, default=50, help='Limit number of PDB files to download')
    parser.add_argument('--base_dir', type=str, default=os.getcwd(), help='Base directory to save PDB files to')    
    args = parser.parse_args()
    
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
    
    if args.symmetry_shape in space_groups:
        print(f"Select a space group for symmetry shape '{args.symmetry_shape}':")
        for idx, sg in enumerate(space_groups[args.symmetry_shape], 1):
            print(f"{idx}. {sg}")
        
        sg_choice = int(input("Enter the number of your chosen space group: "))
        if 1 <= sg_choice <= len(space_groups[args.symmetry_shape]):
            selected_space_group = space_groups[args.symmetry_shape][sg_choice - 1]
            print(f"You have selected space group '{selected_space_group}'.")
            print(f"Retrieving up to {args.limit} PDB IDs for space group '{selected_space_group}'...")
            
            pdb_ids = get_pdb_ids(selected_space_group, args.symmetry_shape, args.limit)
            
            downloader = ProteinDownloader(args.base_dir)
            downloader.download_files(pdb_ids, selected_space_group)
        else:
            print("Invalid choice. Please run the script again and select a valid number.")
    else:
        print(f"Invalid symmetry shape '{args.symmetry_shape}'. Available options are: {', '.join(space_groups.keys())}")

if __name__ == "__main__":
    main()