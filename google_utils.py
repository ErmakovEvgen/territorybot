import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Подключение через сервисный ключ
def get_worksheet(sheet_id: str):
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("service_account.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    return sheet.sheet1  # первая вкладка
