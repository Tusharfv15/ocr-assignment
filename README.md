# Image Text and Table Extraction

This project implements OCR (Optical Character Recognition) and table extraction from images using multiple approaches. It processes images to extract both text content and tabular data, saving the results in structured formats.

## Features

### Text Extraction using Pytesseract

- Utilizes Pytesseract OCR engine for text extraction
- Creates image annotations
- Extracts text content from images
- Generates detailed JSON reports
- Output stored in `output/image_name/` directory

### Table Extraction using Docling

- Leverages IBM's Docling library for converting image data to markdown
- Implements regex patterns to identify and extract tables from markdown
- Saves tables in both markdown and JSON formats
- Tables stored in `output/image_name/tables/` directory
- Note: Tables directory is only created for images containing tabular data

## Output Format

### Tables
- Each table is saved in two formats:
  - Markdown (.md): Human-readable format
  - JSON (.json): Structured data format with headers and rows

### Directory Structure
- Output is organized by image name
- Tables are only extracted and saved when present in the image
- Each image's extracted content is stored in its own directory

## Notes
- The tables directory will only be created for images that contain tabular data
- The script automatically handles various image formats (jpg, jpeg, png, tiff, bmp)
- Errors and processing status are logged to the console


