import fitz  # PyMuPDF
import re


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

def process_matches(matches, information, sum_threshold):
    sum = 0
    for match in matches:
        try:
            category, percentage, each = match
            total_percentage = 0
            key = category.lower().title()
        
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
        
            if total_percentage + float(percentage) <= sum_threshold or not key.startswith("second_"):
                information[key] = float(percentage)
                total_percentage += float(percentage)
            else:
                print(f"Skipping '{key}' as adding the current percentage exceeds {sum_threshold}%.")
        
            sum += float(percentage)
        except Exception as e:
            print(f"Error processing match: {e}")

    return sum

def extract_assignments(file_content):
    information = {}
    sum_threshold = 100

    

    pattern = r"(\b(?:labs|exam[12]|project|quizzes|attendance|exams|homework|final)\b|\w+\s*[-]?\s*\w*\s*(?:quiz|report|assignments|participation|drawing|visit|contour|prelectures|checkpoints|final|quizzes|exam\w*|homework|labs|exercises|exam1|count for|worth|lab|midterm)\b).*?(\d+(?:[.]\d+)?)%(\s*each)?"
    pattern += r"(?!.*?\b(?:dropped|extension|on the departmental|on the final|of your final)\b)"
    pattern_2 = r"(\b(?:labs|exam[12]|project|quizzes|attendance|homework)\b|\w+\s*[-]?\s*\w*\s*(?:quiz|contour|drawing|report|prelectures|checkpoints|final|quizzes|exam\w*|homework|labs|exercises|exam1|count for|worth|lab|midterm)\b).*?(\d+(?:[.]\d+)?)pts(\s*each)?"
    pattern_3 = r"(?:\b(\w+)\s+\1\b.*?)(?:\d+(?:[.]\d+)?%.*?(\d+(?:[.]\d+)?)%|\d+(?:[.]\d+)%)( )"
    pattern_4 = r"(\b(?:labs|exam[12]|project|quizzes|attendance|exams|homework|final)\b|\w+\s*[-]?\s*\w*\s*(?:quiz|report|drawing|contour|prelectures|checkpoints|final|quizzes|exam\w*|homework|labs|exercises|exam1|count for|worth|lab|midterm)\b).*?(\d+(?:[.]\d+)?)%(\s*each)?"

    matches = re.findall(pattern, file_content, re.IGNORECASE)
    matches_2 = re.findall(pattern_2, file_content, re.IGNORECASE)
    
    if len(matches_2) > len(matches):
        matches = matches_2

    count = 0
    for i in range(len(matches)):
        if count + float(matches[i][1]) > 100:
            matches = matches[:i]
            break
        else:
            count += float(matches[i][1]) 
        
    # Process initial matches
    sum = process_matches(matches, information, sum_threshold)
    
    # If the sum is still less than 100, add pattern_3 matches
    if sum < sum_threshold:
        matches_3 = re.findall(pattern_3, file_content, re.IGNORECASE)
        sum += process_matches(matches_3, information, sum_threshold - sum)

    # If the sum is still less than 100, add pattern_4 matches
    if sum < sum_threshold:
        matches_4 = re.findall(pattern_4, file_content, re.IGNORECASE)
        process_matches(matches_4, information, sum_threshold - sum)

    return information



def main():
        
    pdf_path = 'syllabus12.pdf'
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
