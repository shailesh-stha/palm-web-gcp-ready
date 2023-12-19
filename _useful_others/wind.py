# Third-party library imports
import time
import streamlit as st
import leafmap
import netCDF4 as nc
import numpy as np
import geopandas as gpd
import xarray as xr
from pyproj import Proj, transform

# Start clock to test out site load time
start_time = time.time()

# Define Page layout
st.set_page_config(page_title="Mikroklima-Visualisierung",
                   layout="centered",
                   initial_sidebar_state="collapsed") #collapsed/expanded

# Import CSS style
with open('./css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    file = r"./data_test/konstanz_4096x4096_v4_3d_N03.000.nc"
    domain = file
    
    # Read netcdf data and origin coordinates from metadata
    output_nc_dataset = nc.Dataset(domain, mode='r')
    origin_x, origin_y, origin_z = output_nc_dataset.origin_x, output_nc_dataset.origin_y, output_nc_dataset.origin_z
    netcdf_data = leafmap.read_netcdf(domain)
    
    def transform_coordinates(coordinates_x, coordinates_y):
        # Define the source and target coordinate reference systems
        source_crs = Proj(init='epsg:25832')  # ETRS89 / UTM zone 32N
        target_crs = Proj(init='epsg:4326')   # WGS84
        
        lon_values, lat_values = transform(source_crs, target_crs, coordinates_x, coordinates_y)
        return(lon_values, lat_values)
    
    # Create list of x and y coordinates using origin x and y metadata from netcdf file
    coordinates_x = np.linspace(0, 512, 256)+origin_x
    coordinates_y = np.linspace(0, 512, 256)+origin_y
    lon_values, lat_values = transform_coordinates(coordinates_x, coordinates_y)
    
    # ------------------------------------------------
    band_index = 72
    level = 6
    
    # Define values for u_wind and v_wind variables
    u_wind_data = netcdf_data['u'].isel(time=band_index, zu_3d=level).values
    u_wind = xr.DataArray(u_wind_data, coords={'lat': lat_values, 'lon': lon_values}, dims=('lat', 'lon'), name='u_wind')

    v_wind_data = netcdf_data['v'].isel(time=band_index, zu_3d=level).values
    v_wind = xr.DataArray(v_wind_data, coords={'lat': lat_values, 'lon': lon_values}, dims=('lat', 'lon'), name='v_wind')
    # Define wind_dataset for wind visualization
    wind_dataset = xr.Dataset({'u_wind': u_wind, 'v_wind': v_wind})
    
    lon_lat = [9.175209, 47.661] #x_y
    # Plot global wind using leafmap
    m = leafmap.Map(zoom=17)
    m.set_center(lon_lat[0], lon_lat[1])
    m.add_basemap('Google Satellite')
    m.add_velocity(wind_dataset,
                   zonal_speed='u_wind',
                   meridional_speed='v_wind',
                   level_index = 0,
                   velocity_scale=0.01,
                   display_options= dict({
                       'speedUnit' : 'm/s',
                       'displayEmptyString': 'No velocity data',
                       }),
                   max_velocity=4,
                   name=f"Wind",
                   )    
    m.to_streamlit(width=500, height=500)
    st.write("Executed")    
except:
    st.write("Error")

end_time = time.time()
st.write(f"Time taken to load: {end_time - start_time:.2f} seconds")