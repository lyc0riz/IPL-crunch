import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path
sys.path.append(os.path.abspath(".."))

def save_report_visual(fig, filename, folder_path='../visualization'):
    """
    Saves a matplotlib/seaborn figure in high resolution for reports.
    """
    # Ensure the directory exists
    output_dir = Path(folder_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the full file path
    file_path = output_dir / filename
    
    # Save with tight bounding box (prevents cutoff labels) and high DPI
    fig.savefig(file_path, dpi=300, bbox_inches='tight', transparent=False, facecolor='white')
    
    print(f"Saved: {filename}")