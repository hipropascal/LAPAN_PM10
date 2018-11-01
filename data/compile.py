from netCDF4 import Dataset, date2num, num2date
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import os


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def list_dir(path):
    return sorted([name for name in os.listdir(path)])


def list_file(path):
    return sorted([name for name in os.listdir(path)])


def plot2d(H):
    plt.imshow(H)
    plt.colorbar(orientation='vertical')
    plt.show()


def compile_netcdf_daily():
    # find where is bounding box of indonesia
    coor = Dataset('xy.nc', 'r')
    lon_coor = coor['XDim'][:]
    lat_coor = coor['YDim'][:]
    bound1 = [10.041020, 89.709920]
    bound2 = [-12.544363, 142.150673]
    idx_lon_bound1 = find_nearest(lon_coor, bound1[1])
    idx_lat_bound1 = find_nearest(lat_coor, bound1[0])
    idx_lon_bound2 = find_nearest(lon_coor, bound2[1])
    idx_lat_bound2 = find_nearest(lat_coor, bound2[0])
    lat_bound1 = lat_coor[idx_lat_bound1]
    lon_bound1 = lon_coor[idx_lon_bound1]
    lat_bound2 = lat_coor[idx_lat_bound2]
    lon_bound2 = lon_coor[idx_lon_bound2]
    lat_arr = lat_coor[idx_lat_bound1 - 1:idx_lat_bound2]
    lon_arr = lon_coor[idx_lon_bound1 - 1:idx_lon_bound2]
    len_lat = lat_arr.shape[0]
    len_lon = lon_arr.shape[0]
    file_list = list_file('raw/')
    rootgrp = Dataset('daily.nc', 'w')
    time = rootgrp.createDimension("time", None)
    lat = rootgrp.createDimension("lat", len_lat)
    lon = rootgrp.createDimension("lon", len_lon)
    aod = rootgrp.createDimension("aod", None)
    times = rootgrp.createVariable("time", "f8", ("time",))
    latitudes = rootgrp.createVariable("lat", "f4", ("lat",))
    longitudes = rootgrp.createVariable("lon", "f4", ("lon",))
    aod_dat = rootgrp.createVariable("aod", "f4", ("time", "lat", "lon",), fill_value=0)
    # aod_dat.units = "micron"
    latitudes.units = "degrees north"
    longitudes.units = "degrees east"
    times.units = "days since 2000-01-01"
    times.calendar = "gregorian"
    date = []
    arr_data = np.zeros((len(file_list), len_lat, len_lon,), dtype=np.float)
    for idx, file in enumerate(file_list):
        date_obj = datetime.strptime(file, 'A%Y%j.nc')
        datenum = date2num(date_obj, units=times.units, calendar=times.calendar)
        date.append(datenum)
        aod_root = Dataset('raw/' + file, 'r')
        aod_data = aod_root['AOD_550_Dark_Target_Deep_Blue_Combined_Mean'][idx_lat_bound1 - 1:idx_lat_bound2,
                   idx_lon_bound1 - 1:idx_lon_bound2]
        # plot2d(aod_data)
        # raw_input("Press Enter to continue...")
        arr_data[idx, :] = aod_data[:]
        aod_root.close()
    times[:] = date
    latitudes[:] = lat_arr
    longitudes[:] = lon_arr
    aod_dat[:] = arr_data


def compile_netcdf_monthly():
    # find where is bounding box of indonesia
    daily = Dataset('daily.nc', 'r')
    time_daily = daily['time'][:]
    lat_daily = daily['lat'][:]
    lon_daily = daily['lon'][:]
    aod_daily = daily['aod'][:]
    monthly = Dataset('monthly.nc', 'w')
    time_monthly = monthly.createDimension("time", None)
    lat_monthly = monthly.createDimension("lat", lat_daily.shape[0])
    lon_monthly = monthly.createDimension("lon", lon_daily.shape[0])
    aod_monthly = monthly.createDimension("aod", None)
    times_monthly = monthly.createVariable("time", "f8", ("time",))
    latitudes_monthly = monthly.createVariable("lat", "f4", ("lat",))
    longitudes_monthly = monthly.createVariable("lon", "f4", ("lon",))
    aod_dat_monthly = monthly.createVariable("aod", "f4", ("time", "lat", "lon",), fill_value=0)
    # aod_dat.units = "micron"
    latitudes_monthly.units = "degrees north"
    longitudes_monthly.units = "degrees east"
    times_monthly.units = "days since 2000-01-01"
    times_monthly.calendar = "gregorian"
    daily_date = num2date(time_daily, units="days since 2000-01-01", calendar="gregorian")
    month_mean = []
    month_list = []
    cm = 0
    m_start = 0
    m_end = 0
    for idx, t in enumerate(daily_date):
        nm = t.month
        if cm != nm:
            cm = nm
            m_end = idx - 1
            month_mean.append(np.nanmean(aod_daily[m_start:m_end], axis=0))
            month_list.append(date2num(t, units=times_monthly.units, calendar=times_monthly.calendar))
            m_start = idx
            print 'new month'
        print t
    times_monthly[:] = month_list
    latitudes_monthly[:] = lat_daily
    longitudes_monthly[:] = lon_daily
    aod_dat_monthly[:] = month_mean


if __name__ == '__main__':
    compile_netcdf_daily()
    compile_netcdf_monthly()
