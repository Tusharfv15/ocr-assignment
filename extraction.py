import os
import cv2
import pytesseract
from pytesseract import Output
from PIL import Image, ImageDraw
import json

# Configure paths
INPUT_DIR = "images"
OUTPUT_DIR = "output"

def process_images():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Process all images in input directory
    for img_file in os.listdir(INPUT_DIR):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(INPUT_DIR, img_file)
            print(f"Processing {image_path}...")
            
            try:
                # Create subdirectory for each image's output
                base_name = os.path.splitext(img_file)[0]
                img_output_dir = os.path.join(OUTPUT_DIR, base_name)
                os.makedirs(img_output_dir, exist_ok=True)
                
                # Process the image
                process_single_image(image_path, img_output_dir)
                
            except Exception as e:
                print(f"Error processing {img_file}: {str(e)}")

def process_single_image(image_path, output_dir):
    try:
        # Extract text and metadata
        data = extract_text_and_metadata(image_path)
        
        if not data or not any(data['text']):
            print(f"Warning: No text extracted from {image_path}")
            return
        
        # Extract full text and missed text
        full_text, missed_text = process_text_data(data)
        
        # Save extracted text to a text file
        text_file_path = os.path.join(output_dir, "extracted_text.txt")
        with open(text_file_path, "w", encoding='utf-8') as f:
            f.write(full_text)
        print(f"Text file generated at {text_file_path}")
        
        # Detect document structure
        headers = detect_headers(data)
        
        # Generate visual annotations
        annotated_img_path = os.path.join(output_dir, "annotated_image.png")
        create_annotated_image(image_path, data, annotated_img_path)
        
        # Generate report
        generate_report(full_text, missed_text, headers, output_dir)
        
        # Optional: Add visual style analysis
        analyze_visual_styles(data, output_dir)
        
    except Exception as e:
        print(f"Error in process_single_image: {str(e)}")
        raise

def extract_text_and_metadata(image_path):
    img = cv2.imread(image_path)
    return pytesseract.image_to_data(img, output_type=Output.DICT)

def process_text_data(data):
    try:
        full_text = []
        missed_text = []
        
        if not data or 'text' not in data or 'conf' not in data:
            print("Warning: Invalid data structure in process_text_data")
            return "", []
        
        for i, text in enumerate(data['text']):
            if isinstance(text, str) and text.strip():
                full_text.append(text)
                if int(float(data['conf'][i])) < 70:  # Convert confidence to float first
                    missed_text.append({
                        'text': text,
                        'confidence': int(float(data['conf'][i])),
                        'position': (data['left'][i], data['top'][i])
                    })
        
        return ' '.join(full_text), missed_text
    except Exception as e:
        print(f"Error in process_text_data: {str(e)}")
        return "", []

def detect_headers(data):
    header_candidates = []
    for i in range(len(data['text'])):
        if data['text'][i].strip() and int(data['height'][i]) > 20:
            header_candidates.append({
                'text': data['text'][i],
                'height': data['height'][i],
                'level': data['level'][i],
                'page_num': data['page_num'][i]
            })
    
    # Simple hierarchy detection - adjust thresholds based on your documents
    sorted_headers = sorted(header_candidates, key=lambda x: (-x['height'], x['page_num']))
    hierarchy = {}
    for idx, header in enumerate(sorted_headers):
        hierarchy[header['text']] = f"H{min(idx+1, 3)}"  # H1-H3 with fallback
    
    return hierarchy

def create_annotated_image(image_path, data, output_path):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    for i in range(len(data['text'])):
        if data['text'][i].strip():
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            
            # Draw rectangle and text
            draw.rectangle([x, y, x+w, y+h], outline="red")
            draw.text((x, y-10), data['text'][i], fill="blue")
    
    img.save(output_path)

def analyze_visual_styles(data, output_dir):
    styles = []
    for i in range(len(data['text'])):
        if data['text'][i].strip():
            styles.append({
                'text': data['text'][i],
                'font_height': data['height'][i],
                'font_width': data['width'][i],
                'confidence': data['conf'][i],
                'block_num': data['block_num'][i],
                'line_num': data['line_num'][i]
            })
    
    styles_path = os.path.join(output_dir, "visual_styles.json")
    with open(styles_path, "w", encoding='utf-8') as f:
        json.dump(obj=styles, fp=f, indent=2, ensure_ascii=False)

def generate_report(full_text, missed_text, headers, output_dir):
    try:
        if not isinstance(full_text, str):
            full_text = str(full_text)
        
        report = {
            "extracted_text": full_text,
            "missed_text": missed_text or [],
            "document_structure": headers or {},
            "stats": {
                "total_characters": len(full_text),
                "missed_characters": sum(len(item['text']) for item in (missed_text or [])),
                "header_count": len(headers or {})
            }
        }
        
        report_path = os.path.join(output_dir, "report.json")
        with open(report_path, "w", encoding='utf-8') as f:
            json.dump(obj=report, fp=f, indent=2, ensure_ascii=False)
            
        print(f"Report generated successfully at {report_path}")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        # Print more debug information
        print(f"Report data: {report}")
        raise

if __name__ == "__main__":
    process_images()
    print("Processing complete. Check the output folder for results.")