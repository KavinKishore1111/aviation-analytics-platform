import pandas as pd

PATH = "data/raw/bts_aug2026.csv"

df = pd.read_csv(
    PATH,
    dtype=str,                      # load everything as string first
    keep_default_na=True,           # empty strings -> NaN
)

# Who actually has a cancellation code?
has_code = df["CANCELLATION_CODE"].notna()
print("Rows with CANCELLATION_CODE:", has_code.sum())
print("Of those, CANCELLED distribution:")
print(df.loc[has_code, "CANCELLED"].value_counts(dropna=False))
print("\nCancellation code values:")
print(df.loc[has_code, "CANCELLATION_CODE"].value_counts(dropna=False))

# And who is cancelled?
canc = df["CANCELLED"] == "1.0"
print("\nRows with CANCELLED=1:", canc.sum())
print("Their CANCELLATION_CODE null rate:", df.loc[canc, "CANCELLATION_CODE"].isna().mean())


# Is ARR_DEL15 inverted?
print("ARR_DEL15 values:")
print(df["ARR_DEL15"].value_counts(dropna=False))

# Cross-tab ARR_DEL15 vs ARR_DELAY sign
df["ARR_DELAY_NUM"] = pd.to_numeric(df["ARR_DELAY"], errors="coerce")
print("\nARR_DELAY stats by ARR_DEL15:")
print(df.groupby("ARR_DEL15")["ARR_DELAY_NUM"].describe())

# And the same for DEP
df["DEP_DELAY_NUM"] = pd.to_numeric(df["DEP_DELAY"], errors="coerce")
print("\nDEP_DELAY stats by DEP_DEL15:")
print(df.groupby("DEP_DEL15")["DEP_DELAY_NUM"].describe())
# ---------- 1. shape ----------
print("SHAPE:", df.shape)
print("COLUMNS:", len(df.columns))

# ---------- 2. null rate per column ----------
nulls = pd.DataFrame({
    "null_count": df.isna().sum(),
    "null_rate_%": (df.isna().mean() * 100).round(2),
}).sort_values("null_rate_%", ascending=False)
print("\n=== NULL RATES ===")
print(nulls)

# ---------- 3. CANCELLED / DIVERTED ----------
for col in ["CANCELLED", "DIVERTED"]:
    print(f"\n=== {col} ===")
    print(df[col].value_counts(dropna=False))
    print((df[col].value_counts(dropna=False, normalize=True) * 100).round(2))

# ---------- 4. CANCELLATION_CODE where CANCELLED=1 ----------
canc = df[df["CANCELLED"] == "1.0"]
print("\n=== CANCELLATION_CODE (CANCELLED=1 only) ===")
print(canc["CANCELLATION_CODE"].value_counts(dropna=False))

# ---------- 5. Delay cause non-null counts ----------
delay_cols = ["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY",
              "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

print("\n=== DELAY CAUSE NON-NULL COUNTS ===")
for c in delay_cols:
    print(f"{c}: {df[c].notna().sum()} non-null")

# Are delay-cause rows a subset of ARR_DEL15=1?
arr15 = df["ARR_DEL15"] == "1.0"
any_cause = df[delay_cols].notna().any(axis=1)
print("\nDelay-cause populated AND ARR_DEL15=1 :", (any_cause & arr15).sum())
print("Delay-cause populated AND ARR_DEL15!=1:", (any_cause & ~arr15).sum())
print("ARR_DEL15=1 but NO delay cause         :", (arr15 & ~any_cause).sum())

# ---------- 6. Distinct airports / airlines ----------
orig_ids = set(df["ORIGIN_AIRPORT_ID"].dropna())
dest_ids = set(df["DEST_AIRPORT_ID"].dropna())
print("\nDistinct ORIGIN_AIRPORT_ID:", len(orig_ids))
print("Distinct DEST_AIRPORT_ID  :", len(dest_ids))
print("Union of airport IDs      :", len(orig_ids | dest_ids))
print("Distinct ORIGIN (IATA)    :", df["ORIGIN"].nunique())
print("Distinct DEST   (IATA)    :", df["DEST"].nunique())
print("Distinct OP_UNIQUE_CARRIER:", df["OP_UNIQUE_CARRIER"].nunique())
print(df["OP_UNIQUE_CARRIER"].value_counts())

# ---------- 7. FL_DATE min / max ----------
fl = pd.to_datetime(df["FL_DATE"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
print("\nFL_DATE parse failures:", fl.isna().sum())
print("FL_DATE min:", fl.min())
print("FL_DATE max:", fl.max())