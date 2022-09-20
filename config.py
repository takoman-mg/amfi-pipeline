endpoint_latest     = "https://www.amfiindia.com/spages/NAVAll.txt"
endpoint_history    = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={}&todt={}"

dbparams = {
    "host"      : "",
    "database"  : "",
    "user"      : "",
    "password"  : ""
}

headerdict = {
    "Scheme Code"                   :   "scheme_code",
    "Scheme Name"                   :   "scheme_name",
    "ISIN Div Payout/ISIN Growth"   :   "isin_div_payout_growth",
    "ISIN Div Payout/ ISIN Growth"  :   "isin_div_payout_growth",
    "ISIN Div Reinvestment"         :   "isin_div_reinvestment",
    "Net Asset Value"               :   "nav",
    "Repurchase Price"              :   "repurchase_price",
    "Sale Price"                    :   "sale_price",
    "Date"                          :   "nav_date"
}

temp_file_path = "/tmp/navdata.csv"

nav_table = "nav_data"
nav_temp_table = "temp_nav_data"