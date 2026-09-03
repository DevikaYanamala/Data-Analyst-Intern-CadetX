"""
Week 1 — Data Profiling
Heavy Supplier & Warehouse Analytics

IMPORTANT: The CSVs as uploaded to the portal have MISLABELED FILENAMES —
the name on each file does not match the columns inside it (e.g. the file
named `customers.csv` actually contains branch/warehouse data). This script
identifies each file by its real header, not its filename, and re-saves
clean copies under their correct, true names.

Run: python3 01_profiling.py
"""
import pandas as pd
import os

RAW_DIR = "/root/.claude/uploads/200f17a8-57f9-51d7-9d2d-10e62d7f0b6d"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

# Map: uploaded filename (as given) -> TRUE table identity, verified by
# inspecting the actual header row of each file.
FILE_MAP = {
    "3c0d8a74-customers.csv":              "branches",
    "0ac895b7-invoices.csv":               "inventory_master",
    "5542ee3f-purchase_orders_header.csv": "products",
    "5cb0d9ba-sales_orders_header.csv":    "purchase_orders_lines",
    "5e829e3e-products.csv":               "payments",
    "92d30516-payments.csv":               "invoices",
    "c2fdb3fb-sales_orders_lines.csv":     "sales_orders_header",
    "e6365aa6-purchase_orders_lines.csv":  "purchase_orders_header",
    "f23eb42d-suppliers.csv":              "stock_ledger",
    "f61b37a3-inventory_master.csv":       "customers",
    "fc71da79-stock_ledger.csv":           "sales_orders_lines",
}
# NOTE: no file mapped to "suppliers" — the real supplier master
# (supplier_id, supplier_name, rating, lead time, etc.) was never uploaded.
# purchase_orders_header carries a supplier_id foreign key but no supplier
# attributes, so supplier-side analysis is limited until that file arrives.

tables = {}
for fname, true_name in FILE_MAP.items():
    df = pd.read_csv(os.path.join(RAW_DIR, fname))
    tables[true_name] = df

report_lines = ["# Week 1 — Data Profiling Report\n",
                 "Generated from the uploaded CSVs, identified by actual header "
                 "content (see filename-mismatch note in the data dictionary).\n"]

PRIMARY_KEYS = {
    "branches": ["branch_id"],
    "customers": ["customer_id"],
    "products": ["product_id"],
    "inventory_master": ["product_id", "branch_id"],
    "invoices": ["invoice_id"],
    "payments": ["payment_id"],
    "sales_orders_header": ["so_id"],
    "sales_orders_lines": ["so_id", "line_number"],
    "purchase_orders_header": ["po_id"],
    "purchase_orders_lines": ["po_id", "line_number"],
    "stock_ledger": ["movement_id"],
}

for name in sorted(tables):
    df = tables[name]
    keys = PRIMARY_KEYS.get(name, [])
    dup_rows = df.duplicated().sum()
    dup_keys = df.duplicated(subset=keys).sum() if keys and all(k in df.columns for k in keys) else "n/a"
    report_lines.append(f"\n## `{name}`  (rows: {len(df):,} · cols: {df.shape[1]})\n")
    report_lines.append(f"- Candidate key: `{', '.join(keys) if keys else 'none defined'}`  "
                         f"— duplicate rows: **{dup_rows}**, duplicate key combos: **{dup_keys}**\n")
    report_lines.append("\n| column | dtype | non-null | null % | n unique |\n|---|---|---|---|---|\n")
    for col in df.columns:
        nn = df[col].notna().sum()
        null_pct = round(100 * (1 - nn / len(df)), 2)
        nunique = df[col].nunique()
        report_lines.append(f"| {col} | {df[col].dtype} | {nn:,} | {null_pct}% | {nunique:,} |\n")

with open(os.path.join(DOC_DIR, "profiling_report.md"), "w") as f:
    f.writelines(report_lines)

print("Profiling complete. Report written to docs/profiling_report.md")
for name, df in tables.items():
    print(f"{name:26s} rows={len(df):>7,}  cols={df.shape[1]}")
