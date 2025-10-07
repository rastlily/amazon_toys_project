import pandas as pd
import numpy as np

# -----------------
# 1. Load cleaned files
wooden = pd.read_csv("wooden_toys_cleaned_2025-09-15.csv")
baby = pd.read_csv("baby_toys_cleaned_2025-09-15.csv")
sustainable = pd.read_csv("sustainable_toys_cleaned_2025-09-15.csv")

# 2. Add toy_type column
wooden['toy_type'] = 'wooden'
baby['toy_type'] = 'baby'
sustainable['toy_type'] = 'sustainable'

# 3. Define desired columns
desired_columns = [
    'asin', 'url', 'title', 'price', 'old_price', 'discount', 'stock',
    'reviews_count', 'age_tuple', 'dimensions_cm', 'weight_grams', '€/g',
    'short_description', 'toy_type'
]

# 4. Ensure all DataFrames have all desired columns
for i, df in enumerate([wooden, baby, sustainable]):
    for col in desired_columns:
        if col not in df.columns:
            df[col] = None
    if i == 0:
        wooden = df[desired_columns]
    elif i == 1:
        baby = df[desired_columns]
    else:
        sustainable = df[desired_columns]

# 5. Concatenate all DataFrames
all_toys = pd.concat([wooden, baby, sustainable], ignore_index=True)

# -----------------
# 6. Convert stock column to numeric (replace 'unlimited' with NaN)
all_toys['stock'] = pd.to_numeric(all_toys['stock'].replace('unlimited', np.nan), errors='coerce')

# 7. Convert numeric columns (price, old_price, weight_grams, €/g)
numeric_cols = ['price', 'old_price', 'weight_grams', '€/g']
for col in numeric_cols:
    all_toys[col] = all_toys[col].apply(lambda x: float(str(x).replace(',', '.')) if pd.notnull(x) else np.nan)

# -----------------
# 8. Save merged dataset for Python analysis
all_toys.to_csv("toys_fisher_price_merged.csv", index=False)

# 9. Save CSV for Excel / Google Sheets (semicolon separator, keep comma for decimals)
all_toys.to_csv("toys_fisher_price_merged_excel.csv", index=False, sep=";", encoding="utf-8-sig")

# 10. Save pretty Excel file with formatting
output_file = "toys_fisher_price_merged.xlsx"

with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    all_toys.to_excel(writer, index=False, sheet_name="Toys")
    workbook  = writer.book
    worksheet = writer.sheets["Toys"]

    # Wrap text for description
    wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})

    # Set column widths
    worksheet.set_column("A:A", 12)   # asin
    worksheet.set_column("B:B", 20)   # url
    worksheet.set_column("C:C", 40)   # title
    worksheet.set_column("D:E", 10)   # price, old_price
    worksheet.set_column("F:F", 10)   # discount
    worksheet.set_column("G:G", 10)   # stock
    worksheet.set_column("H:H", 12)   # reviews_count
    worksheet.set_column("I:I", 15)   # age_tuple
    worksheet.set_column("J:K", 15)   # dimensions_cm, weight_grams
    worksheet.set_column("L:L", 10)   # €/g
    worksheet.set_column("M:M", 50, wrap_format)  # short_description
    worksheet.set_column("N:N", 12)   # toy_type

print("✅ Merged dataset saved in 3 formats: CSV (Python), CSV (Excel), XLSX with formatting.")






