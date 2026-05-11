import pandas as pd

try:
    df = pd.read_excel('data/nigeria_agri_yield_cleaned-updated.xlsx')
    with open('data_info.txt', 'w') as f:
        f.write(f"Columns: {df.columns.tolist()}\n")
        f.write(f"Head:\n{df.head().to_string()}\n")
        f.write(f"Info:\n")
        df.info(buf=f)
    print("Data info written to data_info.txt")
except Exception as e:
    print(e)
