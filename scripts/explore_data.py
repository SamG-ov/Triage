"""
Phase 1: load the Bitext customer-support dataset and inspect it.

We are NOT building anything yet. We just want to understand:
  - what columns exist and what they contain
  - how many rows there are
  - the class balance (how many tickets per category)
  - whether there are duplicates
  - how long a typical ticket is

Run:  python scripts/explore_data.py
"""

# Use the Windows system certificate store so HTTPS works behind antivirus/proxy
# TLS interception. Must run before any network request.
import truststore
truststore.inject_into_ssl()

import pandas as pd
from datasets import load_dataset

# 1. Load the dataset from Hugging Face. It downloads once, then caches locally.
#    We convert it to a pandas DataFrame because pandas is great for inspection.
print("Loading dataset (first run downloads ~tens of MB, then cached)...")
ds = load_dataset("bitext/Bitext-customer-support-llm-chatbot-training-dataset", split="train")
df = ds.to_pandas()

# 2. Shape = (rows, columns). The first number is how many tickets we have.
print("\n=== SHAPE (rows, columns) ===")
print(df.shape)

# 3. What are the columns, and what does one row actually look like?
print("\n=== COLUMNS ===")
print(list(df.columns))

print("\n=== ONE EXAMPLE ROW ===")
example = df.iloc[0]
for col in df.columns:
    value = str(example[col])
    preview = value if len(value) <= 200 else value[:200] + "..."
    print(f"  {col}: {preview}")

# 4. CLASS BALANCE: how many tickets per category?
#    If one category dominates, accuracy numbers can be misleading.
print("\n=== CLASS BALANCE: tickets per category ===")
print(df["category"].value_counts())

print("\n=== finer breakdown: tickets per intent ===")
print(df["intent"].value_counts())

# 5. DUPLICATES: are there repeated ticket texts?
#    Duplicates inflate accuracy and waste API calls.
n_total = len(df)
n_unique_text = df["instruction"].nunique()
print("\n=== DUPLICATES ===")
print(f"  total rows:            {n_total}")
print(f"  unique ticket texts:   {n_unique_text}")
print(f"  exact-duplicate texts:  {n_total - n_unique_text}")

# 6. LENGTH: how long is a typical ticket (in characters)?
#    Long tickets cost more tokens; very short ones may be too vague.
lengths = df["instruction"].str.len()
print("\n=== TICKET LENGTH (characters) ===")
print(lengths.describe())
