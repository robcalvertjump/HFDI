import numpy as np
import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pickle
import pathlib

#### Lon-lat lookup ####################################################

if pathlib.Path('appdata/lonlat_lookup.pkl').is_file():
    lonlat_lookup_dict = pickle.load( open( "appdata/lonlat_lookup.pkl", "rb" ) )
else:
    lonlat_lookup_dict = {}

geolocator = Nominatim(user_agent="HFDI")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=3)

def lookup_lonlat(practice_code, address_tuple):
    if not practice_code in lonlat_lookup_dict:
        retrieve_lonlat(practice_code, address_tuple)
        save_state()
    
    return lonlat_lookup_dict[practice_code]

def retrieve_lonlat(practice_code, address_tuple):
    adr1, adr2, adr3, adr4, postcode = address_tuple
    country = "England"
    print(address_tuple)
    address_attemps = []
    if pd.isnull(adr4):
        address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [adr1, adr2, adr3, adr4, postcode, country] )) ))
    address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [adr1, adr2, adr3, postcode, country] )) ))
    address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [adr2, adr3, postcode, country] )) ))
    address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [adr1, adr2, postcode, country] )) ))
    address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [adr2, postcode, country] )) ))
    address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [postcode, country] )) ))
    address_attemps.append( ", ".join( list(filter(lambda d: not pd.isnull(d), [adr1, country] )) ))

    for address_str in address_attemps:
        location = geocode(address_str)

        if not location is None:
            lonlat_lookup_dict[practice_code] = (location.longitude, location.latitude)
            return

    raise Exception("Address not searchable:", address_tuple)

def save_state():
    pickle.dump( lonlat_lookup_dict, open( "appdata/lonlat_lookup.pkl", "wb" ) )

def clear_state():
    lonlat_lookup_dict = {}
    save_state()