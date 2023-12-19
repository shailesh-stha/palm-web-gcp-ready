# Third-party library imports
import leafmap # leafmap==0.29.6 keplergl==0.3.2
import netCDF4 as nc
import numpy as np
import xarray as xr
from pyproj import Proj, transform
import streamlit as st

def wind_streamline(time_index_wind, level_index_wind, display_image):
    file = r"./data/netcdf/3D/konstanz_4096x4096_v4_3d_N03_reduced.000.nc"
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
    band_index = time_index_wind
    time_index = band_index * 3
    period = "am" if time_index < 12 else "pm"
    
    level = level_index_wind
    level_sequence = [4,6,8,10,12,16,18,20] # 0=4, 7=20
    elevation = 2 * level_sequence[level]
    
    # Define values for u_wind and v_wind variables
    u_wind_data = netcdf_data['u'].isel(time=band_index, zu_3d=level).values
    u_wind = xr.DataArray(u_wind_data, coords={'lat': lat_values, 'lon': lon_values}, dims=('lat', 'lon'), name='u_wind')

    v_wind_data = netcdf_data['v'].isel(time=band_index, zu_3d=level).values
    v_wind = xr.DataArray(v_wind_data, coords={'lat': lat_values, 'lon': lon_values}, dims=('lat', 'lon'), name='v_wind')
    # Define wind_dataset for wind visualization
    wind_dataset = xr.Dataset({'u_wind': u_wind, 'v_wind': v_wind})
    
    # Plot Leafmap
    m = leafmap.Map(zoom=17)
    lon_lat = [9.175209, 47.660850] #x_y
    m.set_center(lon_lat[0], lon_lat[1])
    
    # Add Basemap
    m.add_basemap('Google Satellite')
    # m.add_basemap('CartoDB.DarkMatter')
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
                   name=f"Wind at {band_index*3} {period}, {origin_z + elevation:.2f}m ",
                   )

    # Add Image Overlay
    if display_image:
        image_url = r"./images/base_simulation_alpha_075/N03/base_1800.png"
        bounds_N03 = [[47.6588733206033766, 9.1718298413872255],
                      [47.6634905475628230, 9.1786643808656230]]
        m.image_overlay(image_url, bounds_N03, name="2m air Temperature")
    
    m.to_streamlit(width=None, height=750)
    
def wind_streamline2(time_index_wind, time, level_index_wind, level, display_image):
    netcdf_file = r"./data/netcdf/3D/reduced.nc"
    netcdf_data = leafmap.read_netcdf(netcdf_file)
    
    with nc.Dataset(netcdf_file, mode="r") as ds_reduced:
        max_u = np.nanmax(ds_reduced['u'][time_index_wind,level_index_wind,:,:])
        max_v = np.nanmax(ds_reduced['u'][time_index_wind,level_index_wind,:,:])
        max_velocity = (max_u**2+max_v**2)**0.5
        # st.write(max_u, max_v, max_velocity)
        if max_velocity < 0.6:
            velocity_scale = 0.05
        elif max_velocity < 1.2:
            velocity_scale = 0.03
        elif max_velocity < 1.75:
            velocity_scale = 0.015
        else:
            velocity_scale = 0.011
        
        test = (ds_reduced['lon'][128], ds_reduced['lat'][115])
        lon_lat = (test[0].item(), test[1].item())
    
    # Subsetting the data to reduce density
    lon_step = 1  # Change this value to adjust the density
    lat_step = 1  # Change this value to adjust the density
    subset_data = netcdf_data.isel(lat=slice(None, None, lat_step), lon=slice(None, None, lon_step))
    
    period = "am" if int(time.replace(":","")) < 1200 else "pm"
    
    m = leafmap.Map(zoom=17)
    m.set_center(lon_lat[0], lon_lat[1])
    m.add_basemap('Google Satellite')
    
    # Add velocity
    m.add_velocity(netcdf_data,
                   zonal_speed='u',
                   meridional_speed='v',
                   latitude_dimension='lat',
                   longitude_dimension='lon',
                   level_dimension='lev',
                   level_index=level_index_wind,
                   time_index=time_index_wind,
                   velocity_scale=velocity_scale,
                   display_options= dict({
                       'speedUnit' : 'm/s',
                    #    'displayEmptyString': 'No velocity data',
                       }),
                   max_velocity=3,
                   name=f"Wind at {time}{period} ",
                   )
    # Add Image Overlay
    if display_image:
        image_url = r"./images/base_simulation_alpha_075/N03/base_1800.png"
        bounds_N03 = [[47.6588733206033766, 9.1718298413872255],
                      [47.6634905475628230, 9.1786643808656230]]
        m.image_overlay(image_url, bounds_N03, name="2m air Temperature")
    m.to_streamlit(width=None, height=750)