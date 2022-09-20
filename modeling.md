## Data modelling

# Database considerations

Decided to use PostgreSQL over columnar dbs, due to the following:
- Given the amount of the data (~2 million records/year), there should not be any significant performance differences purely based on scale
- Columnar databases will have an advantage in terms of storage/data compression, due to the repeating fields in several columns
- Few query scenarios using aggregations, compared to queries directly accessing data based on dates


# Schema design

nav_data
- scheme_name
- scheme_code
- ISIN_div_payout_growth
- ISIN_div_reinvestment
- nav
- nav_date

Observations
- This single table will hold both historical and incremental data
- Schema can be normalized further
	- Separate tables for mutual funds, scheme types, schemes
	- Mapping table for mutual fund x scheme type x scheme

# Performance Optimizations
- Use (scheme_code, nav_date) as primary key, since queries are primarily concentrated on schemes
- To optimize queries for a particular scheme, we can create individual indexes on scheme_code and related fields
- Indexes will affect write performance, which should be acceptable since the pipeline is read-heavy
- Table can be partitioned based on nav_date, scheme_code or mutual fund based on the requirement. However, since partition creation is a manual step in PostgreSQL, additional coding and planning required

# Table definitions
```sql
CREATE TABLE nav_data (
    scheme_name text NOT NULL,
    scheme_code integer NOT NULL,
    ISIN_div_payout_growth text,
    ISIN_div_reinvestment text,
    nav real,
    nav_date date NOT NULL,
    PRIMARY KEY (scheme_code, nav_date)
) PARTITION BY RANGE (nav_date);
-- Create partitions for every required year
CREATE TABLE nav_data_y2022 PARTITION OF nav_data FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');
CREATE TABLE nav_data_y2021 PARTITION OF nav_data FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE nav_data_y2020 PARTITION OF nav_data FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');

CREATE TABLE temp_nav_data (
    scheme_name text ,
    scheme_code integer ,
    ISIN_div_payout_growth text,
    ISIN_div_reinvestment text,
    nav text,
	repurchase_price text,
    sale_price text,
    nav_date date
);
```