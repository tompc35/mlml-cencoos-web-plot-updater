# %% [markdown]
# # Interannual variability at Moss Landing seawater intake
# 
# Analysis of water property anomalies since 2010. Data is available at http://seawater.mlml.calstate.edu
# 
# The csv files have been compiled and stored in NetCDF format, which can be easily loaded into an xarray Dataset (http://xarray.pydata.org/en/stable/). See readme file for details on how to automatically download all csv files and produce a NetCDF file. MLML physoce package is available at https://github.com/physoce/physoce-py. 

# %%
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import xarray as xr
import pandas as pd
import mlml_data_path
import matplotlib.dates as mdates
import os

import sys
sys.path.append('mlml-shorestation-processing/msp/moss_landing/')
from mlml import read_csv_data, cleanup_raw, add_flags

# %% [markdown]
# ### Load dataset

# %%
nc_dir = 'Data/MLML_shore_stations/moss_landing/netcdf/'
station_dir = 'Data/MLML_shore_stations/moss_landing/csv/'

# # read data in csv files to xarray dataset
ds = read_csv_data(station_dir, format='dataset')

# # specify location of readme file and add metadata to dataset
# # readme_file = station_dir + '1_README.TXT'
# # d = add_metadata(ds, station, readme_file)

# # Additional processing
# ds = cleanup_raw(ds)
# ds = add_flags(ds)

ds = xr.open_mfdataset(nc_dir+'*.nc')
ds.load()

# %% [markdown]
# ### QARTOD and calibration
# 
# Apply flags from QARTOD tests to all variables. Use only data flagged as 1 (*Pass; Data have passed critical real-time quality control tests and are deemed adequate for use as preliminary data*)
# 
# Calibration dates for C and T sensors are obtained from data readme file and maintenance log.

# %%
var_list = ['ba','cond','do2','fluor','osat','otemp','ph','sal','temp','trans']

for var in var_list:
    flagi = np.where(ds[var + '_flg'] != 1)
    ds[var][flagi] = np.nan
    


# %% [markdown]
# ### Monthly climatology and anomalies
# 
# Calculate monthly means. Use monthly means to compute seasonal climatology. Subtract seasonal cycle to obtain monthly anomalies.

# %%
# sw1dr = ds.rolling()
sw5min = ds.resample(time='5min').mean()
sw5min_interp = sw5min.interpolate_na('time', limit=24)

# swh = sw5min_interp.resample(time='1h').median()

swd = sw5min_interp.resample(time='1D').mean()
swd_frac = (np.isfinite(sw5min_interp)).resample(time='1D').sum()/(12*24)
swd_good = swd.where(swd_frac['temp'] > 0.5)
swd_good_past = swd.where((swd_frac['temp'] > 0.5) & (swd['time.year'] <= 2025))

sw5dr = swd_good.rolling(time=5, center=True, min_periods=1).mean()

climd = sw5dr.groupby('time.dayofyear').mean('time')
climd90pct = sw5dr.groupby('time.dayofyear').quantile(0.9, 'time')
climd10pct = sw5dr.groupby('time.dayofyear').quantile(0.1, 'time')
anomd = swd_good.groupby('time.dayofyear') - climd


# %%
swm = swd_good.resample(time='1MS').mean()
swm_frac = (np.isfinite(swd_good)).resample(time='1MS').sum()/(xr.ones_like(swd_good)).resample(time='1MS').sum()
swm_good = swm.where(swm_frac['temp'] > 0.5)
swm_good_past = swm.where((swm_frac['temp'] > 0.5) & (swm['time.year'] <= 2025))

clim = swm_good_past.groupby('time.month').mean('time')
anom = swm_good.groupby('time.month') - clim

# %% [markdown]
# # Temperature variability (2010-2016)

# %%
climd['temp'][-1] = 0.5*(climd['temp'][0] + climd['temp'][-2])
climd90pct['temp'][-1] = 0.5*(climd90pct['temp'][0] + climd90pct['temp'][-2])
climd10pct['temp'][-1] = 0.5*(climd10pct['temp'][0] + climd10pct['temp'][-2])

# %%
clim_rep = np.tile(climd['temp'], 3)
clim_rep90pct = np.tile(climd90pct['temp'], 3)
clim_rep10pct = np.tile(climd10pct['temp'], 3)

# %%
clim_smooth = np.convolve(clim_rep, np.ones(31)/31, 'same')
clim_smooth90pct = np.convolve(clim_rep90pct, np.ones(31)/31, 'same')
clim_smooth10pct = np.convolve(clim_rep10pct, np.ones(31)/31, 'same')

# %%
climd['temp_smooth'] = (('dayofyear'), clim_smooth[366:2*366])
climd90pct['temp_smooth'] = (('dayofyear'), clim_smooth90pct[366:2*366])
climd10pct['temp_smooth'] = (('dayofyear'), clim_smooth10pct[366:2*366])

# %%
dates = pd.date_range(start="2026-01-01", periods=366)
swd_2026 = swd_good.where(swd_good['time'] >= np.datetime64('2026-01-01'))

dates25 = pd.date_range(start="2025-01-01", periods=366)
swd_25_26 = swd_good.where(swd_good['time'] >= np.datetime64('2025-01-01'))
swd_2025 = swd_good.where((swd_good['time'] >= np.datetime64('2025-01-01')) & 
                          (swd_good['time'] < np.datetime64('2026-01-01')))

days = (dates-np.datetime64('2026-01-01'))/np.timedelta64(1, 'D')

# %%
plt.figure(figsize=(8, 3))
#plt.plot(swd_good['time'].dt.dayofyear, swd_good['temp'], '.', color='gray', markersize=4)
plt.plot(swd_2026['time'], swd_2026['temp'], 'r-')
plt.plot(dates, climd['temp_smooth'], 'k-')
plt.plot(dates, climd90pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
plt.plot(dates, climd10pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
fmt = mdates.DateFormatter('%b')
plt.gca().xaxis.set_major_formatter(fmt)
plt.xlim([np.datetime64('2026-01-01'), np.datetime64('2026-12-31')])

if os.path.exists('figures/') == False:
    os.mkdir('figures/')

# %%
fig,ax = plt.subplots(figsize=(8, 3))
ax.plot(swd_good['time'].dt.dayofyear.astype('datetime64[D]'), swd_good['temp'], 
         '.', color='gray', markersize=5, alpha=0.2, markeredgewidth=0, label='historical')
ax.plot(((swd_2026['time']-np.datetime64('2026-01-01'))/np.timedelta64(1, 'D')+1).astype('datetime64[D]'), 
         swd_2026['temp'], 'r-', label='2026')
# plt.plot(((swd_2025['time']-np.datetime64('2025-01-01'))/np.timedelta64(1, 'D')+1).astype('datetime64[D]'), 
#          swd_2025['temp'], '-', color='gray')
ax.plot(days, climd['temp_smooth'], 'k-', label='climatological mean (2010-2025)')
ax.plot(days, climd90pct['temp_smooth'], linestyle='--', color='k', linewidth=1, label='10th/90th percentiles')
ax.plot(days, climd10pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
fmt = mdates.DateFormatter('%b')
ax.xaxis.set_major_formatter(fmt)
ax.set_xlim([np.datetime64('1970-01-01'), np.datetime64('1970-12-31')])
ax.set_ylabel('[$\\degree$C]')
update_str = pd.to_datetime(swd_good['time'].values[-1]).strftime('%Y-%m-%d')
ax.set_title('MLML seawater intake temperature - daily averages\nupdated '+ update_str)
axf = ax.twinx()
y1, y2 = ax.get_ylim()
axf.set_yticks(np.arange(45, 70, 5))
axf.set_ylim(y1*9/5+32, y2*9/5+32)
axf.set_ylabel('[$\\degree$F]')
ax.legend(fontsize=6)
plt.tight_layout()
plt.savefig('figures/temperature_recent_seasonal_historical.png')

# %%
plt.figure(figsize=(8, 3))
#plt.plot(swd_good['time'].dt.dayofyear, swd_good['temp'], '.', color='gray', markersize=4)
plt.plot(swd_25_26['time'], swd_25_26['temp'], 'r-')
plt.plot(dates25, climd['temp_smooth'], 'k-')
plt.plot(dates25, climd90pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
plt.plot(dates25, climd10pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
plt.plot(dates, climd['temp_smooth'], 'k-')
plt.plot(dates, climd90pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
plt.plot(dates, climd10pct['temp_smooth'], linestyle='--', color='k', linewidth=1)
fmt = mdates.DateFormatter('%b')
plt.gca().xaxis.set_major_formatter(fmt)
plt.xlim([np.datetime64('2025-01-01'), np.datetime64('2026-12-31')])

# %%
plt.figure()
plt.subplot(211)
plt.plot(ds['time'],ds['temp'],lw=0.5)
plt.plot(swd_good['time'],swd_good['temp'])
plt.title('MLML temperature - 5 min data and daily means')
plt.ylabel('$T$ [$^o$C]')

plt.subplot(212)
plt.plot(anom['time'],anom['temp'],lw=2)
plt.plot(np.array([anom['time'].values[0],
                   anom['time'].values[-1]]),
         np.array([0,0]),'k--')
plt.title('MLML temperature - monthly anomalies')
plt.ylabel('$T$ anomaly [$^o$C]')
plt.tight_layout()
plt.savefig('figures/interannual_T.png', dpi=800)

# %%



