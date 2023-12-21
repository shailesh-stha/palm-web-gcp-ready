# Third-party library imports
import leafmap # leafmap==0.29.6 keplergl==0.3.2
import netCDF4 as nc
import numpy as np
import streamlit as st

def wind_streamline2(time_index_wind, time, level_index_wind, level, display_image):
    netcdf_file = r"./data/netcdf/3D/reduced.nc"
    netcdf_data = leafmap.read_netcdf(netcdf_file)
    
    with nc.Dataset(netcdf_file, mode="r") as ds_reduced:
        max_u = np.nanmax(ds_reduced['u'][time_index_wind,level_index_wind,:,:])
        max_v = np.nanmax(ds_reduced['u'][time_index_wind,level_index_wind,:,:])
        max_velocity = (max_u**2+max_v**2)**0.5
        # st.write(max_u, max_v, max_velocity)
        velocity_dict = {0.68: 0.06,
                         1.15: 0.050,
                         1.17: 0.030,
                         1.95: 0.025,
                         2.70: 0.016,
                         3.50: 0.0125,}
        for key in velocity_dict:
            if max_velocity < key:
                velocity_scale = velocity_dict[key]
                break
            else:
                velocity_scale = 0.005
        
                
        test = (ds_reduced['lon'][128], ds_reduced['lat'][115])
        lon_lat = (test[0].item(), test[1].item())
    
    period = "am" if int(time.replace(":","")) < 1200 else "pm"
    
    st.write(max_velocity)
    
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
                       'displayEmptyString': 'No velocity data',
                       }),
                   max_velocity=3,
                   name=f"Wind at {time}{period} ",
                   )

    if display_image:
        image_url = r"./images/base_simulation_alpha_075/N03/base_1800.png"
        bounds_N03 = [[47.6588733206033766, 9.1718298413872255],
                      [47.6634905475628230, 9.1786643808656230]]
        m.image_overlay(image_url, bounds_N03, name="2m air Temperature")
    m.to_streamlit(width=None, height=800)