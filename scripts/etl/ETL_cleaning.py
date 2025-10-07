import pandas as pd
import numpy as np
import re

#------------------------------------------------------------
#BABY_TOYS_CLEENING
#------------------------------------------------------------


# 1. Load raw CSV
df = pd.read_csv("baby_toys_raw_2025-09-15.csv")

# 2. Remove duplicates by ASIN
df = df.drop_duplicates(subset="asin")

# 3. Clean title: remove "Fisher-Price"
df["title"] = df["title"].str.replace(r"(?i)^Fisher-Price\s*", "", regex=True)

# 4. Price / old_price -> European format with comma
def clean_price(x):
    if pd.isna(x) or x == "":
        return ""
    x = str(x).replace("€", "").strip()
    x = x.replace(".", ",")  # decimal dot to comma
    x = re.sub(r"[^\d,]", "", x)
    return x

df["price"] = df["price"].apply(clean_price)
df["old_price"] = df["old_price"].apply(clean_price)

# 5. Discount -> number or empty
def clean_discount(x):
    if pd.isna(x) or x == "":
        return ""
    x = str(x).replace("%", "").replace("-", "").strip()
    return x if re.match(r"^\d+(\,\d+)?$", x.replace(".", ",")) else ""

df["discount"] = df["discount"].apply(clean_discount)

# 6. Stock -> number or "unlimited"
def parse_stock(x):
    if pd.isna(x) or x.strip() == "" or "In stock" in str(x):
        return "unlimited"
    match = re.search(r"\d+", str(x))
    if match:
        return int(match.group())
    return "unlimited"

df["stock"] = df["stock"].apply(parse_stock)

# 7. Reviews_count -> extract number only
def parse_reviews(x):
    if pd.isna(x) or x.strip() == "":
        return 0
    match = re.search(r"\d+", str(x).replace(",", ""))
    return int(match.group()) if match else 0

df["reviews_count"] = df["reviews_count"].apply(parse_reviews)

# Helper: format age without .0 if integer
def format_age(val):
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    elif isinstance(val, int):
        return str(val)
    else:
        return str(val)

# 8. Age_range -> convert months to years, handle warnings correctly
def parse_age(x, weight_text=""):
    ages_min = []
    ages_max = []
    combined = str(x) + " " + str(weight_text)
    combined = combined.lower()
    # Extract ages from warning
    warning_match = re.findall(r"under (\d+) months", combined)
    for w in warning_match:
        ages_min.append(round(int(w) / 12))

    # Extract explicit ranges: separate months and years
    ranges = re.findall(r"(\d+)\s*(month|year)", combined)
    for n, unit in ranges:
        n = int(n)
        if unit == "month":
            n = round(n / 12)
        if ages_min == []:
            ages_min.append(n)
        ages_max.append(n)
    if not ages_min and not ages_max:
        return ""

    min_age = min(ages_min) if ages_min else min(ages_max)
    max_age = max(ages_max) if ages_max else min_age
    return f"{format_age(min_age)}-{format_age(max_age)}" if min_age != max_age else format_age(min_age)

df["age_range"] = df.apply(lambda row: parse_age(row["age_range"], row.get("weight", "")), axis=1)

# 9. Dimensions and Weight (weight rounded to integer type)
def parse_dimensions_weight(x):
    if pd.isna(x):
        return pd.Series([np.nan, np.nan])

    x_lower = x.lower()
    # remove warning text
    x_lower = re.sub(r"warning.*", "", x_lower)

    # Weight extraction
    weight_match = re.search(r"(\d+\.?\d*)\s*(kg|g)", x_lower)
    weight = np.nan
    if weight_match:
        w, unit = weight_match.groups()
        weight = float(w.replace(",", "."))  # Ensure decimal point for conversion
        if unit == "kg":
            weight *= 1000
        weight = int(round(weight))  # int

    # Dimensions: take first 3 numbers as is
    dims_match = re.findall(r"(\d+\.?\d*)", x_lower)
    dims = ""
    if len(dims_match) >= 3:
        dims = " x ".join(dims_match[:3])

    return pd.Series([dims, weight])

df[["dimensions_cm", "weight_grams"]] = df["weight"].apply(parse_dimensions_weight)

# Drop original weight column
df = df.drop(columns=["weight"])

# 10. Price per gram €/g rounded to 2 decimals and formatted with comma
def compute_price_per_gram(price, weight):
    if price == "" or pd.isna(weight) or weight == 0 or pd.isna(price):
        return ""
    p = float(price.replace(",", "."))
    price_per_gram = round(p / weight, 2)
    return str(price_per_gram).replace(".", ",")  # Convert to European format

df["€/g"] = df.apply(lambda row: compute_price_per_gram(row["price"], row["weight_grams"]), axis=1)

# Convert weight_grams to string with comma for European format
def format_european_number(x):
    if pd.isna(x):
        return ""
    return str(x).replace(".", ",")

df["weight_grams"] = df["weight_grams"].apply(format_european_number)

# 11. Move short_description to last column
cols = [c for c in df.columns if c != "short_description"] + ["short_description"]
df = df[cols]

# 12. Save cleaned CSV
df.to_csv("baby_toys_cleaned_2025-09-15.csv", index=False)

print("Cleaning completed, file saved: baby_toys_cleaned_2025-09-15.csv")

#------------------------------------------------------------
#WOODEN_TOYS_CLEENING
#------------------------------------------------------------

# 1. Load raw CSV
df = pd.read_csv("wooden_toys_raw_2025-09-15.csv")

# 2. Remove duplicates by ASIN
df = df.drop_duplicates(subset="asin")

# 3. Clean title: remove "Fisher-Price"
df["title"] = df["title"].str.replace(r"(?i)^Fisher-Price\s*", "", regex=True)

# 4. Price / old_price -> European format with comma
def clean_price(x):
    if pd.isna(x) or x == "":
        return ""
    x = str(x).replace("€", "").strip()
    x = x.replace(".", ",")  # decimal dot to comma
    x = re.sub(r"[^\d,]", "", x)
    return x

df["price"] = df["price"].apply(clean_price)
df["old_price"] = df["old_price"].apply(clean_price)

# 5. Discount -> number or empty
def clean_discount(x):
    if pd.isna(x) or x == "":
        return ""
    x = str(x).replace("%", "").replace("-", "").strip()
    return x if re.match(r"^\d+(\,\d+)?$", x.replace(".", ",")) else ""

df["discount"] = df["discount"].apply(clean_discount)

# 6. Stock -> number or "unlimited"
def parse_stock(x):
    if pd.isna(x) or x.strip() == "" or "In stock" in str(x):
        return "unlimited"
    match = re.search(r"\d+", str(x))
    if match:
        return int(match.group())
    return "unlimited"

df["stock"] = df["stock"].apply(parse_stock)

# 7. Reviews_count -> extract number only
def parse_reviews(x):
    if pd.isna(x) or x.strip() == "":
        return 0
    match = re.search(r"\d+", str(x).replace(",", ""))
    return int(match.group()) if match else 0

df["reviews_count"] = df["reviews_count"].apply(parse_reviews)

# Helper: format age without .0 if integer
def format_age(val):
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    elif isinstance(val, int):
        return str(val)
    else:
        return str(val)

# 8. Age_range -> convert months to years, handle warnings correctly
def parse_age(x, weight_text=""):
    ages_min = []
    ages_max = []
    combined = str(x) + " " + str(weight_text)
    combined = combined.lower()
    # Extract ages from warning
    warning_match = re.findall(r"under (\d+) months", combined)
    for w in warning_match:
        ages_min.append(round(int(w) / 12))

    # Extract explicit ranges: separate months and years
    ranges = re.findall(r"(\d+)\s*(month|year)", combined)
    for n, unit in ranges:
        n = int(n)
        if unit == "month":
            n = round(n / 12)
        if ages_min == []:
            ages_min.append(n)
        ages_max.append(n)
    if not ages_min and not ages_max:
        return ""

    min_age = min(ages_min) if ages_min else min(ages_max)
    max_age = max(ages_max) if ages_max else min_age
    return f"{format_age(min_age)}-{format_age(max_age)}" if min_age != max_age else format_age(min_age)

df["age_range"] = df.apply(lambda row: parse_age(row["age_range"], row.get("weight", "")), axis=1)

# 9. Dimensions and Weight (weight rounded to integer type)
def parse_dimensions_weight(x):
    if pd.isna(x):
        return pd.Series([np.nan, np.nan])

    x_lower = x.lower()
    # remove warning text
    x_lower = re.sub(r"warning.*", "", x_lower)

    # Weight extraction
    weight_match = re.search(r"(\d+\.?\d*)\s*(kg|g)", x_lower)
    weight = np.nan
    if weight_match:
        w, unit = weight_match.groups()
        weight = float(w.replace(",", "."))  # Ensure decimal point for conversion
        if unit == "kg":
            weight *= 1000
        weight = int(round(weight))  # int

    # Dimensions: take first 3 numbers as is
    dims_match = re.findall(r"(\d+\.?\d*)", x_lower)
    dims = ""
    if len(dims_match) >= 3:
        dims = " x ".join(dims_match[:3])

    return pd.Series([dims, weight])

df[["dimensions_cm", "weight_grams"]] = df["weight"].apply(parse_dimensions_weight)

# Drop original weight column
df = df.drop(columns=["weight"])

# 10. Price per gram €/g rounded to 2 decimals and formatted with comma
def compute_price_per_gram(price, weight):
    if price == "" or pd.isna(weight) or weight == 0 or pd.isna(price):
        return ""
    p = float(price.replace(",", "."))
    price_per_gram = round(p / weight, 2)
    return str(price_per_gram).replace(".", ",")  # Convert to European format

df["€/g"] = df.apply(lambda row: compute_price_per_gram(row["price"], row["weight_grams"]), axis=1)

# Convert weight_grams to string with comma for European format
def format_european_number(x):
    if pd.isna(x):
        return ""
    return str(x).replace(".", ",")

df["weight_grams"] = df["weight_grams"].apply(format_european_number)

# 11. Move short_description to last column
cols = [c for c in df.columns if c != "short_description"] + ["short_description"]
df = df[cols]

# 12. Save cleaned CSV
df.to_csv("wooden_toys_cleaned_2025-09-15.csv", index=False)

print("Cleaning completed, file saved: baby_toys_cleaned_2025-09-15.csv")

#------------------------------------------------------------
#SUSTAINABLE_TOYS_CLEENING
#------------------------------------------------------------

# 1. Load raw CSV
df = pd.read_csv("sustainable_toys_raw_2025-09-15.csv")

# 2. Remove duplicates by ASIN
df = df.drop_duplicates(subset="asin")

# 3. Clean title: remove "Fisher-Price"
df["title"] = df["title"].str.replace(r"(?i)^Fisher-Price\s*", "", regex=True)

# 4. Price / old_price -> European format with comma
def clean_price(x):
    if pd.isna(x) or x == "":
        return ""
    x = str(x).replace("€", "").strip()
    x = x.replace(".", ",")  # decimal dot to comma
    x = re.sub(r"[^\d,]", "", x)
    return x

df["price"] = df["price"].apply(clean_price)
df["old_price"] = df["old_price"].apply(clean_price)

# 5. Discount -> number or empty
def clean_discount(x):
    if pd.isna(x) or x == "":
        return ""
    x = str(x).replace("%", "").replace("-", "").strip()
    return x if re.match(r"^\d+(\,\d+)?$", x.replace(".", ",")) else ""

df["discount"] = df["discount"].apply(clean_discount)

# 6. Stock -> number or "unlimited"
def parse_stock(x):
    if pd.isna(x) or x.strip() == "" or "In stock" in str(x):
        return "unlimited"
    match = re.search(r"\d+", str(x))
    if match:
        return int(match.group())
    return "unlimited"

df["stock"] = df["stock"].apply(parse_stock)

# 7. Reviews_count -> extract number only
def parse_reviews(x):
    if pd.isna(x) or x.strip() == "":
        return 0
    match = re.search(r"\d+", str(x).replace(",", ""))
    return int(match.group()) if match else 0

df["reviews_count"] = df["reviews_count"].apply(parse_reviews)

# Helper: format age without .0 if integer
def format_age(val):
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    elif isinstance(val, int):
        return str(val)
    else:
        return str(val)

# 8. Age_range -> convert months to years, handle warnings correctly
def parse_age(x, weight_text=""):
    ages_min = []
    ages_max = []
    combined = str(x) + " " + str(weight_text)
    combined = combined.lower()
    # Extract ages from warning
    warning_match = re.findall(r"under (\d+) months", combined)
    for w in warning_match:
        ages_min.append(round(int(w) / 12))

    # Extract explicit ranges: separate months and years
    ranges = re.findall(r"(\d+)\s*(month|year)", combined)
    for n, unit in ranges:
        n = int(n)
        if unit == "month":
            n = round(n / 12)
        if ages_min == []:
            ages_min.append(n)
        ages_max.append(n)
    if not ages_min and not ages_max:
        return ""

    min_age = min(ages_min) if ages_min else min(ages_max)
    max_age = max(ages_max) if ages_max else min_age
    return f"{format_age(min_age)}-{format_age(max_age)}" if min_age != max_age else format_age(min_age)

df["age_range"] = df.apply(lambda row: parse_age(row["age_range"], row.get("weight", "")), axis=1)

# 9. Dimensions and Weight (weight rounded to integer type)
def parse_dimensions_weight(x):
    if pd.isna(x):
        return pd.Series([np.nan, np.nan])

    x_lower = x.lower()
    # remove warning text
    x_lower = re.sub(r"warning.*", "", x_lower)

    # Weight extraction
    weight_match = re.search(r"(\d+\.?\d*)\s*(kg|g)", x_lower)
    weight = np.nan
    if weight_match:
        w, unit = weight_match.groups()
        weight = float(w.replace(",", "."))  # Ensure decimal point for conversion
        if unit == "kg":
            weight *= 1000
        weight = int(round(weight))  # int

    # Dimensions: take first 3 numbers as is
    dims_match = re.findall(r"(\d+\.?\d*)", x_lower)
    dims = ""
    if len(dims_match) >= 3:
        dims = " x ".join(dims_match[:3])

    return pd.Series([dims, weight])

df[["dimensions_cm", "weight_grams"]] = df["weight"].apply(parse_dimensions_weight)

# Drop original weight column
df = df.drop(columns=["weight"])

# 10. Price per gram €/g rounded to 2 decimals and formatted with comma
def compute_price_per_gram(price, weight):
    if price == "" or pd.isna(weight) or weight == 0 or pd.isna(price):
        return ""
    p = float(price.replace(",", "."))
    price_per_gram = round(p / weight, 2)
    return str(price_per_gram).replace(".", ",")  # Convert to European format

df["€/g"] = df.apply(lambda row: compute_price_per_gram(row["price"], row["weight_grams"]), axis=1)

# Convert weight_grams to string with comma for European format
def format_european_number(x):
    if pd.isna(x):
        return ""
    return str(x).replace(".", ",")

df["weight_grams"] = df["weight_grams"].apply(format_european_number)

# 11. Move short_description to last column
cols = [c for c in df.columns if c != "short_description"] + ["short_description"]
df = df[cols]

# 12. Save cleaned CSV
df.to_csv("sustainable_toys_cleaned_2025-09-15.csv", index=False)

print("Cleaning completed, file saved: baby_toys_cleaned_2025-09-15.csv")
