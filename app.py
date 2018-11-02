from flask import Flask, render_template, jsonify, send_file
from netCDF4 import Dataset, date2num, num2date
from datetime import datetime
import src.rasterize as ras
from StringIO import StringIO
import numpy as np

app = Flask(__name__)
monthly = Dataset('data/monthly.nc')
aod_monthly = monthly['aod'][:]
lats = monthly['lat'][:]
lons = monthly['lon'][:]
daily = Dataset('data/daily.nc')
aod_daily = daily['aod'][:]
units = "days since 2000-01-01"
calendar = "gregorian"
time_daily = daily['time'][:]
time_monthly = monthly['time'][:]

bound = {'top': 11.5, 'bottom': -11.5, 'left': 88.5, 'right': 141.5}


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/raster/daily/<time>')
def req_raster_date(time):
    time_obj = datetime.strptime(time, '%d-%m-%Y')
    time_num = date2num(time_obj, units, calendar)
    idx_time = find_nearest(time_daily, time_num)
    img_io = StringIO()
    img = ras.to_raster(np.nan_to_num(aod_daily[idx_time].filled()), bound)
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/timeseries/daily/<time_start>/<time_end>/<lat>_<lon>')
def req_timeseries_daily(time_start, time_end, lat, lon):
    time_obj_start = datetime.strptime(time_start, '%d-%m-%Y')
    time_obj_end = datetime.strptime(time_end, '%d-%m-%Y')
    time_num_start = date2num(time_obj_start, units, calendar)
    time_num_end = date2num(time_obj_end, units, calendar)
    idx_time_start = find_nearest(time_daily, time_num_start)
    idx_time_end = find_nearest(time_daily, time_num_end)
    idx_lat = find_nearest(lats, float(lat))
    idx_lon = find_nearest(lons, float(lon))
    datas = np.round(aod_daily[idx_time_start:idx_time_end, idx_lat, idx_lon].filled(),decimals=3)
    datas[datas < 0] = 0
    vecfmt = np.vectorize(stringify)
    dates = num2date(time_daily[idx_time_start:idx_time_end],units,calendar)
    dates_list = [datetime.strftime(date, '%Y%m%d') for date in dates]
    return jsonify({'time': dates_list, 'data': vecfmt(datas).tolist()})


@app.route('/raster/monthly/<time>')
def req_raster_month(time):
    time_obj = datetime.strptime(time, '%d-%m-%Y')
    time_num = date2num(time_obj, units, calendar)
    idx_time = find_nearest(time_monthly, time_num)
    img_io = StringIO()
    img = ras.to_raster(np.nan_to_num(aod_monthly[idx_time].filled(0)), bound)
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/timeseries/monthly/<time_start>/<time_end>/<lat>_<lon>')
def req_timeseries_monthly(time_start, time_end, lat, lon):
    time_obj_start = datetime.strptime(time_start, '%d-%m-%Y')
    time_obj_end = datetime.strptime(time_end, '%d-%m-%Y')
    time_num_start = date2num(time_obj_start, units, calendar)
    time_num_end = date2num(time_obj_end, units, calendar)
    idx_time_start = find_nearest(time_daily, time_num_start)
    idx_time_end = find_nearest(time_daily, time_num_end)
    idx_lat = find_nearest(lats, float(lat))
    idx_lon = find_nearest(lons, float(lon))
    datas = np.round(aod_monthly[idx_time_start:idx_time_end, idx_lat, idx_lon].filled(),decimals=3)
    datas[datas < 0] = 0
    vecfmt = np.vectorize(stringify)
    dates = num2date(time_monthly[idx_time_start:idx_time_end],units,calendar)
    dates_list = [datetime.strftime(date, '%Y%m%d') for date in dates]
    return jsonify({'time': dates_list, 'data': vecfmt(datas).tolist()})


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def stringify(r):
    if r == 0:
        return '0'
    else:
        return "%.3f" % (r,)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181)
