import pandas as pd
import os

tv_series_df = pd.read_csv(os.path.join('data','tv_series_final_first_clean'))
tv_series_df_clean = pd.DataFrame()

at_row = 0
for index, row in tv_series_df.iterrows():
    year_list = tv_series_df.loc[index,'Year']
    title = tv_series_df.loc[index,'Title']
    year_list = str(year_list).split()
    for year in year_list:
        if year != 'nan':
            int_year = int(year)
            if 1978 < int_year < 2019:
                at_row+=1
                tv_series_df_clean.loc[at_row,'Title'] = title
                tv_series_df_clean.loc[at_row,'Year']  = int_year

tv_series_df_clean.sort_values('Year',inplace=True)
tv_series_df_clean.drop_duplicates(inplace=True)
tv_series_df_clean.reset_index(inplace=True)
print(tv_series_df_clean.head())
print(tv_series_df_clean.tail())

tv_series_df.to_csv(os.path.join('data','tv_series_final_clean'))