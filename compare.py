
import pandas as pd
import openpyxl
import os
def normalize_value(value):
    try:
        num = float(value)
        if num.is_integer():  
            return str(int(num)) 
        return str(num) 
    except (ValueError, TypeError):  
        return str(value)  

def read_report(file_path):
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        return pd.read_excel(file_path, engine='openpyxl')



def compare_reports(files):
    dataframes = []
    file_names = [os.path.basename(file) for file in files]  # Lấy tên file

    for file in files:
        df = read_report(file)
        dataframes.append(df)
    
    num_rows = len(dataframes[0])
    num_files = len(dataframes)

    differences = []

    for row_index in range(num_rows):
        for column in dataframes[0].columns:
            compare_values = []
            for file_index in range(num_files):
                value = normalize_value(dataframes[file_index].iloc[row_index][column])
                compare_values.append((file_names[file_index], value))  # Chỉ lấy tên file

            unique_values = set(value for _, value in compare_values)
            if len(unique_values) > 1:
                diff_string = f"Dòng {row_index + 1} | Cột '{column}' | " + " | ".join(
                    [f"{file}: {value}" for file, value in compare_values]
                )
                differences.append(diff_string)

    return differences