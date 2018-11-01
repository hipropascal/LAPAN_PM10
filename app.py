from flask import Flask, render_template, jsonify, send_file
from netCDF4 import Dataset, date2num
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
def req_timeseries_daily(time_start, time_end,lat,lon):
    time_obj_start = datetime.strptime(time_start, '%d-%m-%Y')
    time_obj_end = datetime.strptime(time_end, '%d-%m-%Y')
    time_num_start = date2num(time_obj_start, units, calendar)
    time_num_end = date2num(time_obj_end, units, calendar)
    idx_time_start = find_nearest(time_daily, time_num_start)
    idx_time_end = find_nearest(time_daily, time_num_end)
    idx_lat = find_nearest(lats, float(lat))
    idx_lon = find_nearest(lons, float(lon))
    data = aod_daily[idx_time_start:idx_time_end,idx_lat,idx_lon].filled().tolist()
    return jsonify({'time':'','data':data})


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


@app.route('/timeseries/daily/<month_start>/<month_end>')
def req_timeseries_monthly(month_start, month_end):
    return True


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


if __name__ == '__main__':
    app.run()
