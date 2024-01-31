from pdf_extraction import extract_text_from_pdf_pymupdf, clean_text, extract_assignments
from google_export import update_google_sheet


def main():
    pdf_path = 'syllabus1.pdf'
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

            
            update_google_sheet(assignments)

    except FileNotFoundError:
        print(f"File '{output_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
