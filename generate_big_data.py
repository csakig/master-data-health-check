import pandas as pd
import numpy as np
import random

# --- CONFIGURATION ---
NUM_ROWS = 500  # Number of rows to generate
ERROR_RATE = 0.05 # 5% error rate per type

print(f"Generating data ({NUM_ROWS} rows)...")

# 1. DATA SEEDS (Mixing these to create realistic names)
prefixes = ["Alpha", "Beta", "Gamma", "Delta", "Omega", "Blue", "Red", "Green", "Global", "Tech", "Smart", "Future", "Rapid", "Prime"]
suffixes = ["Solutions", "Systems", "Corp", "Logistics", "Consulting", "Group", "Holdings", "Soft", "Trade", "Industries"]
legal_forms = ["Kft.", "GmbH", "Inc.", "Ltd.", "Nyrt.", "Zrt.", "AG"]
countries = ["HU", "DE", "US", "AT", "FR", "GB"]

# 2. HELPER FUNCTIONS
def generate_company_name():
    return f"{random.choice(prefixes)} {random.choice(suffixes)} {random.choice(legal_forms)}"

def generate_email(company, country):
    # Create a realistic email derived from the company name
    clean_name = company.split(' ')[0].lower()
    domain = "com" if country == "US" else country.lower()
    return f"info@{clean_name}.{domain}"

def generate_vat(country):
    if country == "HU": return str(random.randint(10000000, 99999999))
    if country == "DE": return "DE" + str(random.randint(100000000, 999999999))
    return str(random.randint(100000, 999999))

# 3. BULK GENERATION
data = []
start_id = 10000

for i in range(NUM_ROWS):
    country = random.choice(countries)
    company = generate_company_name()
    
    row = {
        "Partner_ID": start_id + i,
        "Company_Name": company,
        "Country": country,
        "Email": generate_email(company, country),
        "VAT_Number": generate_vat(country)
    }
    data.append(row)

df = pd.DataFrame(data)

# 4. ERROR INJECTION (To ensure the validator finds issues)

# A) Generate Duplicate IDs
# Take the first 10 rows and append them again to the end
duplicates = df.head(10).copy()
df = pd.concat([df, duplicates], ignore_index=True)
print(f" -> Added 10 duplicate rows.")

# B) Missing Emails (approx 5%)
# Randomly select rows and remove the email
mask_missing_email = np.random.choice([True, False], size=len(df), p=[ERROR_RATE, 1-ERROR_RATE])
df.loc[mask_missing_email, 'Email'] = np.nan
print(f" -> Removed approx. {sum(mask_missing_email)} email addresses.")

# C) Invalid Email Format (approx 2%)
mask_bad_email = np.random.choice([True, False], size=len(df), p=[0.02, 0.98])
# We use an English placeholder text for bad emails
df.loc[mask_bad_email, 'Email'] = "invalid_email_format_missing_at_symbol"
print(f" -> Corrupted approx. {sum(mask_bad_email)} email formats.")

# D) Invalid VAT Number (Too short)
mask_bad_vat = np.random.choice([True, False], size=len(df), p=[0.03, 0.97])
df.loc[mask_bad_vat, 'VAT_Number'] = "123"
print(f" -> Corrupted approx. {sum(mask_bad_vat)} VAT numbers.")

# 5. SAVE TO FILE
file_name = "test_big_data.xlsx"
df.to_excel(file_name, index=False)

print("-" * 30)
print(f"DONE! Created '{file_name}' with {len(df)} rows.")
print("Now upload this file to the App!")