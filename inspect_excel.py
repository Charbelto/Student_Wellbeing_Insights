import pandas as pd

try:
    df = pd.read_excel('app/database/PAI dataset (final).xlsx')
    print("All Columns:", df.columns.tolist())
except Exception as e:
    print(e)
