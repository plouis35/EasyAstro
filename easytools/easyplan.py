"""
 EASYPLAN - display target position & infos
 
 usage :
        plan = EasyPlan(observatory, date, target)

 public variables/methods : 
       <TODO>
       
"""
import matplotlib.pyplot as plt
import numpy as np
from astropy.visualization import astropy_mpl_style, quantity_support
import astropy.units as u
from astroplan.plots import plot_sky
from astroplan.plots import plot_airmass
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
from astropy.coordinates import get_sun
from astropy.coordinates import get_body
from astroplan import Observer
from astroplan import FixedTarget
from IPython.display import display
import ipywidgets as widgets

plt.style.use(astropy_mpl_style)
quantity_support()

def PlotPosition(obs_latitude: float, obs_longitude: float , obs_height: float, obs_date: str, name: str) -> widgets.HBox:
    ### get observatory location
    obs_date = obs_date
    obs_loc = EarthLocation(lat = obs_latitude*u.deg, lon = obs_longitude*u.deg, height = obs_height*u.m)
    utcoffset = +2*u.hour

    ### get coming night times
    midnight = Time(obs_date + ' 00:00:00') - utcoffset
    delta_midnight = np.linspace(-12, 12, 1000)*u.hour
    times_to_tomorow = midnight + delta_midnight
    frame_to_tomorow = AltAz(obstime=times_to_tomorow, location=obs_loc)
    
    ### get SUN position
    sunaltazs_to_tomorow = get_sun(times_to_tomorow).transform_to(frame_to_tomorow)
    
    ### get MOON position
    moon_to_tomorow = get_body("moon", times_to_tomorow)
    moonaltazs_to_tomorow= moon_to_tomorow.transform_to(frame_to_tomorow)
    
    ### get TARGETS position
    targets = [name]
    targets_to_tomorow = [ SkyCoord.from_name(target) for target in targets ]
    targets_altazs_to_tomorow = [t.transform_to(frame_to_tomorow) for t in targets_to_tomorow ]
    
    right_panel = widgets.Output(layout={'width': '46.2%'})#, 'height': '50px'})
    with right_panel:
        #plt.figure(figsize=(8,6))
        plt.plot(delta_midnight, sunaltazs_to_tomorow.alt, color='orange', ls='--', label='Sun')
        plt.plot(delta_midnight, moonaltazs_to_tomorow.alt, color=[0.75]*3, ls='--', label='Moon')
        for tt,name in zip(targets_altazs_to_tomorow, targets):
            plt.scatter(delta_midnight, tt.alt, c=tt.az.value, label=name, lw=0, s=8, ls='dotted', cmap='viridis')
            #plt.plot(delta_midnight, tt.alt, label=name) #, cmap='viridis')
        plt.fill_between(delta_midnight, 0*u.deg, 90*u.deg, sunaltazs_to_tomorow.alt < -0*u.deg, color='0.5', zorder=0)
        plt.fill_between(delta_midnight, 0*u.deg, 90*u.deg, sunaltazs_to_tomorow.alt < -18*u.deg, color='k', zorder=0)
        plt.colorbar().set_label('Azimuth [deg]')
        plt.legend(loc='upper left')
        plt.xticks((np.arange(13)*2-12)*u.hour)
        plt.ylim(0*u.deg, 90*u.deg)
        plt.xlabel('Hours from EDT Midnight')
        plt.ylabel('Altitude [deg]')
        plt.xlim(-7*u.hour, 10*u.hour)
        plt.show()
    
    left_panel = widgets.Output(layout={'width': '47%'})#, 'height': '550px'})
    with left_panel:
        observe_time = midnight + np.linspace(-4, 6, 10)*u.hour # - + np.linspace(-12, 12, 40)*u.hour
        observer = Observer(location=obs_loc)
        
        #targets = [target_selected.value]
        for name in targets:
            plot_sky(target = FixedTarget.from_name(name), observer = observer, time = observe_time, grid=True) #, north_to_east_ccw = True)
        
        plt.legend(loc='center left', bbox_to_anchor=(1.25, 0.5))
        plt.show()
    
    #display(widgets.HBox([right_panel, left_panel]))
    return (widgets.HBox([right_panel, left_panel]))
    