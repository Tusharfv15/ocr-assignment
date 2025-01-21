import os
import re
import json
from pathlib import Path

# Set environment variable to handle OpenMP runtime conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from docling.document_converter import DocumentConverter

def extract_table_content(markdown_text):
    """Extract tables from markdown text using regex"""
    # Pattern to match markdown tables (including headers and content)
    table_pattern = r'(\|[^\n]+\|\n\|[-:\|\s]+\|\n(?:\|[^\n]+\|\n)+)'
    
    # Find all tables in the text
    tables = re.finditer(table_pattern, markdown_text)
    
    return list(tables)

def save_tables(tables, output_dir):
    """Save extracted tables to separate files"""
    tables_dir = output_dir / 'tables'
    tables_dir.mkdir(exist_ok=True)
    
    for idx, table in enumerate(tables, 1):
        table_content = table.group(1)
        table_file = tables_dir / f'table_{idx}.md'
        
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write(table_content)
        
        # Also save as JSON for easier parsing
        json_file = tables_dir / f'table_{idx}.json'
        table_data = parse_markdown_table(table_content)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(table_data, f, indent=2, ensure_ascii=False)

def parse_markdown_table(table_content):
    """Convert markdown table to structured data"""
    lines = table_content.strip().split('\n')
    
    # Extract headers
    headers = [col.strip() for col in lines[0].split('|')[1:-1]]
    
    # Skip the separator line (|---|---|...)
    data_rows = []
    for line in lines[2:]:
        if line.strip():
            row_data = [col.strip() for col in line.split('|')[1:-1]]
            data_rows.append(row_data)
    
    # Create structured data
    table_data = {
        'headers': headers,
        'rows': data_rows
    }
    
    return table_data

def process_image(image_path):
    """Process a single image and extract tables"""
    try:
        # Create output directory based on image name
        image_name = Path(image_path).stem
        output_dir = Path('output') / image_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert document
        converter = DocumentConverter()
        result = converter.convert(image_path)
        markdown_text = result.document.export_to_markdown()
        
        # Extract and save tables
        tables = extract_table_content(markdown_text)
        if tables:
            save_tables(tables, output_dir)
            print(f"Extracted {len(tables)} tables from {image_name}")
        else:
            print(f"No tables found in {image_name}")
            
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

def extract_tables():
    """Process all images in the images folder"""
    # Get the current working directory and create/check images folder
    current_dir = Path.cwd()
    image_dir = current_dir / "images"
    
    if not image_dir.exists():
        image_dir.mkdir(exist_ok=True)
        print(f"Created images directory at {image_dir}")
        print("Please place your images in this folder and run the script again")
        return
    
    # Process all supported image files
    supported_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    image_files = [f for f in image_dir.glob('*') if f.suffix.lower() in supported_extensions]
    
    if not image_files:
        print(f"No supported images found in {image_dir}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image
    for image_file in image_files:
        print(f"\nProcessing {image_file.name}...")
        process_image(str(image_file))

if __name__ == "__main__":
    extract_tables()