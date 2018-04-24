import pandas as pd
import os

mv_list = []
tv_list = []

mv_frame = pd.read_csv(os.path.join('backup','movies_400'),index_col=None, header=0)
mv_list.append(mv_frame)
mv_frame = pd.read_csv(os.path.join('backup3','movies_1150'),index_col=None, header=0)
mv_list.append(mv_frame)
mv_df = pd.concat(mv_list)

mv_df.to_csv(os.path.join('data','movies_final'))

tv_frame = pd.read_csv(os.path.join('backup','tv_series_244'),index_col=None, header=0)
tv_list.append(tv_frame)
tv_frame = pd.read_csv(os.path.join('backup3','tv_series_810'),index_col=None, header=0)
tv_list.append(tv_frame)

tv_df = pd.concat(tv_list)
tv_df.to_csv(os.path.join('data','tv_series_final'))

