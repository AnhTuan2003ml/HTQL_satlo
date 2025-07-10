import pandas as pd
def du_doan(gio, ngay, thang, luong_mua, file_path='data\\du_doan.csv'):
    thoi_diem = f"{int(thang):02d}-{int(ngay):02d} {int(gio):02d}h"
    try:
        df = pd.read_csv(file_path)
        row = df[df['thoi_diem'] == thoi_diem]
        if row.empty:
            return f"Thấp"
        xac_suat = row['xac_suat_satlo'].values[0]
        mua_tb = row['luong_mua_tb_khi_satlo'].values[0]
        mua_min = row['luong_mua_min_satlo'].iloc[0]
        
        if luong_mua >= mua_min :
            return f'Cao'
        if xac_suat == 0:
            return f"Thấp"

        if luong_mua >= mua_tb:
            return f"Cao"
        else:
            return f"Thấp"

    except FileNotFoundError:
        return 
    
