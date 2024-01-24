import fitz  # PyMuPDF
import re

numbers_spelled = ['one','two','three','four','five','six','seven','eight','nine','ten']
def extract_text_from_pdf_pymupdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    doc.close()
    return text

def clean_text(text):
    # Join lines that are part of the same section based on context
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    cleaned_text = ' '.join(cleaned_lines).replace(":","")
    return cleaned_text

def extract_assignments(file_content):
    information = {}
    
    
    pattern = r"(\b(?:labs|exam[12]|project|quizzes|attendance|homework)\b|\w+\s*[-]?\s*\w*\s*(?:quiz|prelectures|checkpoints|final|quizzes|exam\w*|homework|labs|exam1|count for|worth|lab|midterm)\b).*?(\d+(?:[.]\d+)?)%(\s*each)?"
    pattern += r"(?!.*?\b(?:dropped|extension)\b)"
    matches = re.findall(pattern, file_content, re.IGNORECASE)
    
    for match in matches:
        category, percentage, each = match
        total_percentage = 0
        key = category.lower()
        
        # Check for "each" and multiply by spelled numbers in the category if present
        if each:
            numbers_spelled = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
            for number_word in numbers_spelled:
                if number_word in category.lower():
                    # Multiply by the corresponding numeric value
                    multiplier = numbers_spelled.index(number_word) + 1
                    percentage = float(percentage) * multiplier
                    break
        
        # Check for duplicates and modify key
        while key in information:
            key = f"second_{key}"
        
        if total_percentage + float(percentage) <= 100 or not key.startswith("second_"):
            information[key] = float(percentage)
            total_percentage += float(percentage)
        else:
            print(f"Skipping '{key}' as adding the current percentage exceeds 100%.")
    
    return information

def main():
    pdf_path = 'syllabus6.pdf'
    output_file_path = 'output_cleaned.txt'
    
    
    
    pdf_text_pymupdf = extract_text_from_pdf_pymupdf(pdf_path)
    
    
    cleaned_pdf_text = clean_text(pdf_text_pymupdf)
    
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_pdf_text)
    
    try:
        with open(output_file_path, 'r') as file:
            file_content = file.read().lower()
            
            
            assignments = extract_assignments(file_content)
            
            
            print("Assignment Types and Percentages:")
            for assignment_type, percentage in assignments.items():
                print(f"{assignment_type}: {percentage}%")
            
    except FileNotFoundError:
        print(f"File '{output_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
