import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

def update_google_sheet(assignments):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
    creds = None
    token_path = 'token.json'

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except FileNotFoundError:
        print(f"Token file '{token_path}' not found. Run the authentication flow.")
    except Exception as e:
        print(f"An error occurred while loading credentials: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error running local server for authentication flow: {e}")

        try:
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error saving credentials to file: {e}")

    gc = gspread.authorize(creds)
    new_spreadsheet_title = 'Final Grade Calculator'
    new_spreadsheet = gc.create(new_spreadsheet_title)
    print(f"New Spreadsheet '{new_spreadsheet_title}' created.")

    worksheet = new_spreadsheet.get_worksheet(0)
    print(f"Using default worksheet '{worksheet.title}'.")

    worksheet.append_row(['|||||','Assignments','Percentage', 'Weight', 'Grade','Final Grade'])

    for assignment_type, percentage in assignments.items():
        weight = float(percentage) / 100.0
        worksheet.append_row(['',assignment_type, str(percentage) + '%', weight, '', ''])
        for _ in range(8):
            worksheet.append_row(['|||||', '', '', '', '',''], value_input_option='RAW')
            # Get the current row number after appending the 8 empty rows
        current_row = len(worksheet.get_all_values()) + 1

        avg_formula = f'=AVERAGE(B{current_row-8}:B{current_row-1})'
        weighted_grade_formula = f'=B{current_row} * {weight}'
        worksheet.append_row(['', avg_formula, '', '', weighted_grade_formula, ''],value_input_option='USER_ENTERED')
    
    for _ in range(3):
            worksheet.append_row(['|||||', '', '', '', '',''], value_input_option='RAW')
    prev_row = len(worksheet.get_all_values())
    final_grade_formula = f'=SUM(E2:E{prev_row})'
    final_letter_grade_formula = '=IF(D2>=93,"A",IF(AND(D2>=90, D2<93),"A-",IF(AND(D2>=87, D2<90),"B+",IF(AND(D2>=83, D2<87),"B",IF(AND(D2>=80, D2<83),"B-",IF(AND(D2>=77, D2<80),"C+",IF(AND(D2>=73, D2<77),"C",IF(AND(D2>=70, D2<73),"C-",IF(AND(D2>=67, D2<70),"D+",IF(AND(D2>=60, D2<67),"D+",IF(D2<60,"F")))))))))))'
    worksheet.append_row(['Final Grade', '', '', '', final_grade_formula,final_letter_grade_formula],value_input_option='USER_ENTERED')

    print("Results successfully added to Google Sheet.")