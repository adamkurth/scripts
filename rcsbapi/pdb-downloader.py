import requests
import os
import argparse

def download_pdb(protein_id, output_dir):
    """
    Download a PDB file for a given protein ID.
    
    Args:
        protein_id (str): The PDB ID (e.g., '6lzg')
        output_dir (str): Directory to save the PDB file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Format URL and filename
    url = f"https://files.rcsb.org/download/{protein_id}.pdb"
    output_file = os.path.join(output_dir, f"{protein_id}.pdb")
    
    try:
        # Check if URL is accessible
        response = requests.head(url)
        if response.status_code == 200:
            # Download the file
            response = requests.get(url)
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Successfully downloaded {protein_id} to {output_file}")
        else:
            print(f"Error: Could not access PDB file for {protein_id}")
    except Exception as e:
        print(f"Error downloading {protein_id}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Download PDB file for a given protein ID')
    parser.add_argument('protein_id', type=str, help='Protein ID (e.g., 253L)')
    parser.add_argument('--output_dir', type=str, default='pdb_files', 
                        help='Directory to save PDB files (default: pdb_files)')
    
    args = parser.parse_args()
    
    # Download the PDB file
    download_pdb(args.protein_id.lower(), args.output_dir)

if __name__ == "__main__":
    main()