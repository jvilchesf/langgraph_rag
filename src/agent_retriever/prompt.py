# Standardized fields you want to map to
standard_fields = [
    "Date",
    "Description",
    "Merchant",
    "Product_service",
    "Amount (EUR)",
    "Currency"
]

# Example output format
output_example = """
{
    "Date": "ColumnNameInSample",
    "Description": "ColumnNameInSample",
    "Merchant",     
    "Product_service",
    "Amount (EUR)": "ColumnNameInSample",
    "Currency": "ColumnNameInSample"
}
"""

# Prompt template
prompt = """
I have a CSV file with the following headers:

{headers}

Based on these column headers, please map them to the following standardized fields:

{standard_fields}

**Instructions:**

- Provide your answer **strictly** as a valid JSON object.
- Each standardized field should be mapped to the corresponding column name from the CSV headers.
- If a standardized field is not present in the sample, set its value to some value that might fit.
- **Do not include any explanations, comments, or additional text before or after the JSON.**
- Output **only** the JSON object.

**Example output format:**

{output_example}
"""

prompt_augmented = """
I have a DataFrame containing bank transactions with the following columns:

| Date                 | Description                        | Merchant                  | Product_service                       | Amount (EUR) | Currency |
|----------------------|------------------------------------|---------------------------|---------------------------------------|--------------|----------|
| 2024-11-21 00:00:00  | Dummy                    | PayPal Europe S.a.r.l. et Cie S.C.A... | 1038356944342/. MDION AG, Ihr  bei MED... | -1.99        | EUR      |
| 2024-11-19 00:00:00  | Dummy                    | PayPal Europe S.a.r.l. et Cie S.C.A... | 1038321988189/PP.5854.PP/. DB Vertrieb GmbH, I... | -52.20       | EUR      |
| 2024-11-14 00:00:00  | Dummy. UEBERWEISUNG                | Techniker Krankenkasse    | TK-BuchNr 04407888734 Beitragserstattung | 125.21       | EUR      |
| 2024-11-13 00:00:00  | Dummy. UEBERWEISUNG                |   CONSULTANTS... | AWV- BEACHTEN HOTLINE  () 1234-111 | 10.00        | EUR      |
| 2024-11-13 00:00:00  | Dummy                    | E-Plus Service GmbH ...   | Gebuehr fuer Kombi-Paket S (alt) fuer Ihr Prep... | -7.99        | EUR      |
| ...                  | ...                                | ...                       | ...                                   | ...          | ...      |
| 2024-10-23 12:37:48  | From Dummy SONNY                | TRANSFER                  | Current                               | 15.40        | EUR      |
| 2024-10-23 12:38:18  | To VANESSA Dummy                    | TRANSFER                  | Current                               | -15.00       | EUR      |
| 2024-10-31 17:34:07  | From VANESSA Dummy                  | TRANSFER                  | Current                               | 0.10         | EUR      |
| 2024-11-07 08:51:21  | From VANESSA Dummy                  | TRANSFER                  | Current                               | 10.00        | EUR      |
| 2024-11-07 09:10:17  | To Dummy SONNY                  | TRANSFER                  | Current                               | -9.00        | EUR      |

I need to add the following additional columns based on the Description, Merchant, and Product_service columns:

- Transaction Type
- Merchant Name
- Merchant Category
- Payment Method
- Location
- Recurring
- Budget Category
- Tags
- Notes
- Payment Status

**Instructions:**

1. **Analyze** each row's **Description**, **Merchant**, and **Product_service** columns and **populate** the additional columns accordingly.
2. **Provide your answer strictly** as a Markdown table, including the new columns and don't include the word Markdown at the beggining of the output.
3. **Do not include any explanations, comments, or additional text** before or after the table.
4. If certain information is not available or applicable, use appropriate placeholders such as `N/A`.
5. **Translate** the all table content to english.
6. ** The output must have {len_chunk} number of rows.

**Example Output:**

| Date                 | Description                        | Merchant                  | Product_service                       | Amount (EUR) | Currency | Transaction Type | Merchant Name       | Merchant Category | Payment Method | Location | Recurring | Budget Category | Tags               | Notes                           Payment Status |
|----------------------|------------------------------------|---------------------------|---------------------------------------|--------------|----------|-------------------|---------------------|-------------------|-----------------|----------|-----------|------------------|--------------------|---------------------------------|----------------|-----------------------|-------------------------------|-----------------|
| 2024-11-21 00:00:00  | Dummy                    | PayPal Europe S.a.r.l. et Cie S.C.A... | Dummy/. MEDION AG, Ihr Einkauf bei MED... | -1.99        | EUR      | Debit             | MEDION AG           | Electronics       | Debit Card     | Online   | Yes       | Groceries        | Shopping           | Purchase of electronic goods    | Completed       |
| 2024-11-19 00:00:00  | Dummy                    | PayPal Europe S.a.r.l. et Cie S.C.A... | Dummy/PP.5854.PP/. DB Vertrieb GmbH, I... | -52.20       | EUR      | Debit             | DB Vertrieb GmbH    | Transport         | Bank Transfer  | Germany  | Yes       | Transportation    | Business Expense   | Monthly transport fees          | Completed       |
| 2024-11-14 00:00:00  | GUTSCHR. Dummy                | Dummy Krankenkasse    | TK-BuchNr Dummy Beitragserstattung | 125.21       | EUR      | Credit            | Techniker K.        | Insurance         | Bank Transfer  | Germany  | No        | Insurance         | Reimbursement      | Contribution refund             | Completed       |
| 2024-11-13 00:00:00  | GUTSCHR. Dummy                | Dummy ENVIRONMENTAL CONSULTANTS... | AWV-Dummy BEACHTEN HOTLINE BUNDESBANK (Dummy) 1234-111 | 10.00        | EUR      | Credit            | INIS Environmental   | Utilities         | Bank Transfer  | Germany  | No        | Fees              | Banking Fees       | Reporting compliance fee        | Completed       |
| 2024-11-13 00:00:00  | Dummy                    | E-Plus Service GmbH ...   | Dummy fuer Kombi-Dummy S (alt) fuer Ihr Prep... | -7.99        | EUR      | Debit             | E-Plus Service      | Telecommunications | Debit Card     | Online   | No        | Utilities         | Fees               | Prepaid package fee             |  Completed       |

**Data Chunk for Processing:**

{chunk}

**Please process the above data and return the chunk augmented DataFrame with the additional columns populated as per the instructions.**
"""