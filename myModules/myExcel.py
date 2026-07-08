from datetime import date, datetime, time
import numpy as np
import pandas as pd


IMAGE_SIZE = (800, 800)

EXCEL_COLUMN_ROCKET = '火箭'
EXCEL_COLUMN_NUMBER = '遥号'
EXCEL_COLUMN_DATE = '日期'
EXCEL_COLUMN_TIME = '时间\n（UTC+8）'
EXCEL_COLUMN_LOCATION = '地点'
EXCEL_COLUMN_SPOT = '工位'
EXCEL_COLUMN_RESULT = '结果'
EXCEL_COLUMN_PAYLOAD = '载荷'
EXCEL_COLUMN_REMARKS = '备注'

################################################################################################
def parseExcelSheetLaunch(excelFile, sheetName, onlyFailed=False, withCancel=False, withPredict=False):
    df = pd.read_excel(excelFile, sheetName, header=0, usecols='A:O', dtype={EXCEL_COLUMN_SPOT: str})
    cond1 = True if withCancel else df[EXCEL_COLUMN_RESULT] != '中止'
    cond2 = ~df[EXCEL_COLUMN_RESULT].isna() if not withPredict else ~df[EXCEL_COLUMN_TIME].isna()
    # cond3 = df[myExcel.EXCEL_COLUMN_RESULT] != '成功'
    df = df[cond1 & cond2]
    pd.set_option('future.no_silent_downcasting', True)
    df.replace('-', np.nan, inplace=True) # Replace '-' with NaN
    df.replace([None, np.nan], '', inplace=True) # Replace None with empty string
    return df

################################################################################################
def parseExcelSheetLaunchTime(excelFile, sheetName, columnList):
    df = pd.read_excel(excelFile, sheetName, skiprows=2, header=None, usecols='A:E,J,M', converters={2: lambda x: str(x).replace('\n', '/')})
    df.columns = columnList
    df[columnList] = df[columnList].ffill()
    df = df.dropna(how='all')
    df = df.dropna(subset=[columnList[-1]])
    return df

################################################################################################
def excel_time_to_timedelta(x):
    # Case 1 — already timedelta
    if isinstance(x, pd.Timedelta):
        return x
    # Case 2 — Excel float (fraction of a day)
    if isinstance(x, (float, int)):
        return pd.to_timedelta(x, unit='d')
    # Case 3 — Python datetime.time
    if isinstance(x, time):
        return pd.to_timedelta(
            x.hour * 3600 + x.minute * 60 + x.second,
            unit='s'
        )
    # Case 4 — full datetime.datetime (Excel date+time)
    if isinstance(x, datetime):
        # Excel datetime is [days since 1899] + [time fraction]
        # So convert to float first:
        excel_float = x.toordinal() - date(1899,12,30).toordinal() + \
                      (x.hour*3600 + x.minute*60 + x.second)/86400
        return pd.to_timedelta(excel_float, unit='d')
    # Case 5 — string “hh:mm:ss” or “mm:ss”
    if isinstance(x, str):
        try:
            return pd.to_timedelta(x)
        except:
            pass
    # fallback: NA
    return pd.NaT

