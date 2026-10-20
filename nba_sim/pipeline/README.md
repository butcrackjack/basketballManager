## Consolidate

Consolidate is for calling the functions in extract and storing results in csv files (in nba_sim/data/raw), done in consolidate.py.
convert_raw_to_parquet.py takes each csv (or a specific one if specified) and converts them to parquet file, stored in nba_sim/data/parquet.
data_clean.py makes a couple adjustments to the parquet fields, such as naming and adding booleans.

## Extract

Extract contains the function used to hit the nba APIs (extract.py).

## Validate

Validate is for verifying the parquet courts, both within the same file and between files (validate.py).
