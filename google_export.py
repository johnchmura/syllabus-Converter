import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

def update_google_sheet(assignments):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    token_path = 'token.json'

    # The credentials.json file is the same one you use for service account authentication.
    # Make sure it has the necessary permissions for Google Sheets and Drive API.
    try:
        # Attempt to load existing credentials from the token file.
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

        # Save the credentials for the next run
        try:
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error saving credentials to file: {e}")

    # Now creds is a valid user credential.
    gc = gspread.authorize(creds)

    # Create a new spreadsheet
    new_spreadsheet_title = 'AssignmentTracker'
    new_spreadsheet = gc.create(new_spreadsheet_title)
    print(f"New Spreadsheet '{new_spreadsheet_title}' created.")

    # Get the default worksheet
    worksheet = new_spreadsheet.get_worksheet(0)  # Index 0 represents the default worksheet
    print(f"Using default worksheet '{worksheet.title}'.")

    # Add headers
    worksheet.append_row(['Assignment Type', 'Percentage', 'Weight', 'User Input', 'Weighted Grade'])

    # Add assignment types, percentages, and weights to the sheet
    for assignment_type, percentage in assignments.items():
        weight = float(percentage) / 100.0  # Convert percentage to decimal for weight
        worksheet.append_row([assignment_type, percentage, weight, '', ''])

    # Add rows for user input
    num_assignments = 8
    for _ in range(num_assignments):
        worksheet.append_row(['', '', '', '', ''])

    # Add formulas for average, weighted grade, and final grade
    start_row = 2  # Assuming data starts from row 2
    end_row = start_row + num_assignments - 1
    avg_formula = f'=AVERAGE(D{start_row}:D{end_row})'
    weighted_grade_formula = f'=E{start_row} * C{start_row}'
    final_grade_formula = f'=SUM(F{start_row}:F{end_row})'
    worksheet.append_row(['', '', '', avg_formula[0:], ''])
    worksheet.append_row(['', '', '', weighted_grade_formula[0:], ''])
    worksheet.append_row(['Final Grade', '', '', final_grade_formula[0:], ''])

    print("Results successfully added to Google Sheet.")
