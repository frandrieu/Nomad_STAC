#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Oct 2023

Script to convert a NOMAD footprint into a STAC catalog

@author: fandrieu
"""

from pystac import Catalog, Item, Asset, MediaType, CatalogType, Collection, Extent, SpatialExtent, TemporalExtent, Provider, ProviderRole, Link
from datetime import datetime
import json
from shapely.geometry import mapping
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.eo import EOExtension
from pystac.extensions.eo import Band
import os
import numpy as np
import geopandas as gpd
from pystac.stac_io import DefaultStacIO
from typing import Any
  
class MyCustomStacIo(DefaultStacIO):
    
    class NpJsonEncoder(json.JSONEncoder):
        """Serializes numpy objects as json."""

        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.floating):
                if np.isnan(obj):
                    return None  # Serialized as JSON null.
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super().default(obj)  
      
    def json_dumps(self, json_dict: dict[str, Any], *args: Any, **kwargs: Any) -> str:
        return super().json_dumps(json_dict, cls = self.NpJsonEncoder, *args, **kwargs)

def create_stac_item(file_path, polygon, bbox, start_time_value, lid, item_id):
    # Create a STAC item for each polygon in the GeoJSON file
    item_datetime = start_time_value
    item = Item(
        id=item_id,
        geometry=mapping(polygon),
        bbox=list(bbox),
        datetime=item_datetime,
        properties={},
        #href=lid
    )

    # for the moment, we use that schema on because a fix must be set in the official repo
    item.stac_extensions.append('https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json')
    item.stac_extensions.append('https://stac-extensions.github.io/file/v2.1.0/schema.json')#)
    item.properties['ssys:targets'] = ['Mars']
    
    item.properties['processing:level']='Ancillary Data Record'
    
    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.wkt2 = """GEOGCRS["Mars (2015) - Sphere / Ocentric",
                    DATUM["Mars (2015) - Sphere",
                        ELLIPSOID["Mars (2015) - Sphere", 3396190, 0,
                    LENGTHUNIT["metre", 1, ID["EPSG", 9001]]],
                    ANCHOR["Viking 1 lander : 47.95137 W"]],
                    PRIMEM["Reference Meridian", 0,
                    ANGLEUNIT["degree", 0.0174532925199433, ID["EPSG", 9122]]],
            CS[ellipsoidal, 2],
                AXIS["geodetic latitude (Lat)", north,
    ORDER[1],
                    ANGLEUNIT["degree", 0.0174532925199433]],
                AXIS["geodetic longitude (Lon)", east,
    ORDER[2],
                    ANGLEUNIT["degree", 0.0174532925199433]],
            ID["IAU", 49900, 2015],
            REMARK["Use semi-major radius as sphere radius for interoperability. Source of IAU Coordinate systems:
    doi://10.1007/s10569-017-9805-5"]]"""

    return item

def get_geojson_info(file_path):
    # Read GeoJSON file using geopandas
    gdf = gpd.read_file(file_path)

    # Extract bounding box (bbox) boundaries
    bbox = gdf.total_bounds
    psa_id = ' https://psa.esa.int/psa/#/pages/search?p=' + gdf.iloc[0].get('psa_lid', None)
    
    # Extract start_time from GeoJSON file 
    start_time_str = gdf.iloc[0].get('utc_start_time', None)

    # Parse start_time string to datetime object
    start_time_value = datetime.strptime(start_time_str, '%Y %b %d %H:%M:%S.%f') if start_time_str else None
    # Extract end_time from GeoJSON file 
    end_time_str = gdf.iloc[0].get('utc_end_time', None)
    # Parse end_time string to datetime object
    end_time_value = datetime.strptime(start_time_str, '%Y %b %d %H:%M:%S.%f') if end_time_str else None
    # Extract polygons
    polygons = gdf.geometry.tolist()
    #extract diffraction order 
    order = gdf.iloc[0].get('diffraction_order', None)
    return polygons, bbox, start_time_value, end_time_value, psa_id, order



def create_stac_collection(folder_path, catalog_title='5 day Nomad Collection'):
   # Create a STAC catalog
   
   
    # Example collection creation
    nomad_collection = Collection(
        id="geops_10_days_lno_collection",
        title="10 days lno - PySTAC prototype",
        description="Collection of 10 days of NOMAD data to make a STAC prototype",
        license="CC-BY-SA",
        catalog_type=CatalogType.SELF_CONTAINED,
        extent=Extent(
            spatial=SpatialExtent([-180, -90, 180, 90]),
            temporal=TemporalExtent([
                (datetime(2020, 1, 1), datetime(2024, 12, 31))
            ])
        )
    )
    nomad_collection.extra_fields['mission'] = "ExoMars"
    nomad_collection.extra_fields['platform'] = "LNO"
    nomad_collection.extra_fields['instruments'] = ["NOMAD"]
    
    #### Catalog metadata
        
    LICENSE = 'CC-BY-4.0'
    ACKNOWLEDGMENT = 'ESA/BIRA-IASB/Université Paris-Saclay - GEOPS'
    MISSION = 'ExoMars'
    INSTRUMENTS = ['NOMAD/LNO']
    
    PUBLICATIONS = [
        
            'Thomas et al. (2016) Optical and radiometric models of the NOMAD instrument part II: the infrared channels-SO and LNO. Optics Express, 24(4), 3790-3805. 10.1364/OE.24.003790',
        
       
            'Cruz-Mermy et al. (2022) Calibration of NOMAD on ExoMars Trace Gas Orbiter: Part 3-LNO validation and instrument stability. Planetary and Space Science, 218, 105399. 10.1016/j.pss.2021.105399',
        
    ]
    
    PROVIDERS = [
        Provider(
            name='Géosciences Paris-Saclay',
            roles=[
                ProviderRole.LICENSOR,
                ProviderRole.PROCESSOR,
            ],
            url='https://www.geops.universite-paris-saclay.fr',
        ),
        Provider(
            name='European Space Agency',
            roles=[
                ProviderRole.PRODUCER,
            ],
            url='https://www.esa.int',
        ),
        Provider(
            name='Belgian Institute for Space Aeronomy',
            roles=[
                ProviderRole.PRODUCER,
                ProviderRole.HOST,
            ],
            url='https://www.aeronomie.be',
        ),
    ]
    
    EXTENSIONS =[
            "https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json",
            "https://stac-extensions.github.io/processing/v1.1.0/schema.json"
    ]
    
    PROCESSING = {
        'processing:level': 'Ancillary Data Record',
        
    }
    CATALOG_y2018 = Catalog(
        id='geops_LNO_2018',
        title='ExoMars NOMAD/LNO footprints, year 2018',
        description=(
            'Year 2018 Géosciences Paris-Saclay STAC catalog for the ExoMars NOMAD/LNO datasets footprints (https://www.geops.universite-paris-saclay.fr) '
        ),
        stac_extensions=EXTENSIONS,
        extra_fields={
            'license': LICENSE,
            'acknowledgment': ACKNOWLEDGMENT,
            'mission': MISSION,
            'instruments': INSTRUMENTS,
            'ssys:targets': "Mars",
            'sci:publications': PUBLICATIONS,
        }
    )
    
    CATALOG_y2018.add_links([
        Link(
            rel='copyright',
            target='https://www.geops.universite-paris-saclay.fr',
            media_type=MediaType.HTML,
            title='GEOPS - Université Paris-Saclay',
        ),
        Link(
            rel='sponsor',
            target='https://pdssp.ias.universite-paris-saclay.fr',
            media_type=MediaType.HTML,
            title='Catalogue du Pôle de données et services Surfaces Planétaires (PDSSP)',
        ),
        Link(
            rel='icon',
            target='nomad.jpg',
            media_type=MediaType.JPEG,
            title='NOMAD instrument (credit photo ESA)',
        ),  
          
            
    ])
    
    
    CATALOG_y2018.add_child(nomad_collection)
    
    CATALOG = Catalog(
        id='geops_nomad_lno_catalog',
        title='ExoMars NOMAD/LNO footprints',
        description=(
            'Géosciences Paris-Saclay STAC catalog for the ExoMars NOMAD/LNO datasets footprints (https://www.geops.universite-paris-saclay.fr) '
        ),
        stac_extensions=EXTENSIONS,
        extra_fields={
            'license': LICENSE,
            'acknowledgment': ACKNOWLEDGMENT,
            'mission': MISSION,
            'instruments': INSTRUMENTS,
            'ssys:targets': "Mars",
            'sci:publications': PUBLICATIONS,
        }
    )
    
    CATALOG.add_links([
        Link(
            rel='copyright',
            target='https://www.geops.universite-paris-saclay.fr',
            media_type=MediaType.HTML,
            title='GEOPS - Université Paris-Saclay',
        ),
        Link(
            rel='sponsor',
            target='https://pdssp.ias.universite-paris-saclay.fr',
            media_type=MediaType.HTML,
            title='Catalogue du Pôle de données et services Surfaces Planétaires (PDSSP)',
        ),
        Link(
            rel='icon',
            target='nomad.jpg',
            media_type=MediaType.JPEG,
            title='NOMAD instrument (credit photo ESA)',
        ),  
            
            
    ])
    
    
    CATALOG.add_child(CATALOG_y2018)
    

    CATALOG_geops = Catalog(
        id='geops_catalog_of_catalogs',
        title='Géosciences Paris-Saclay STAC catalogs',
        description=(
            'Catalog of Géosciences Paris-Saclay STAC catalogs (https://www.geops.universite-paris-saclay.fr) '
        ),
        stac_extensions=EXTENSIONS,
        extra_fields={
            'license': LICENSE,
            'acknowledgment': ACKNOWLEDGMENT,
            'mission': MISSION,
            'instruments': INSTRUMENTS,
            'ssys:targets': "Mars",
            'sci:publications': PUBLICATIONS,
        }
    )
    
    CATALOG_geops.add_links([
        Link(
            rel='copyright',
            target='https://www.geops.universite-paris-saclay.fr',
            media_type=MediaType.HTML,
            title='GEOPS - Université Paris-Saclay',
        ),
        Link(
            rel='sponsor',
            target='https://pdssp.ias.universite-paris-saclay.fr',
            media_type=MediaType.HTML,
            title='Catalogue du Pôle de données et services Surfaces Planétaires (PDSSP)',
        ),
        Link(
            rel='icon',
            target='LOGO_GEOPS.jpg',
            media_type=MediaType.JPEG,
            title='GEOPS logo',
        ),  
            
    ])
    
    
    CATALOG_geops.add_child(CATALOG)
    
    
    return CATALOG_geops


def add_items(folder_path, collec, output_dir):
    # Get the list of files in the specified folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".geojson")]

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        polygons, bbox, start_time_value, end_time_value, psa_id, order = get_geojson_info(file_path)
        
        
        # Définir la collection 1
        collection1 = Collection(
            id=file_path,
            title=file_path,
            description="Orbit "+file_path,
            extent=Extent(
                spatial=SpatialExtent(list(bbox)),
                temporal=TemporalExtent([start_time_value, end_time_value])
            ),
            license="proprietary"
        )
        collec.add_child(collection1)
        
        for idx, polygon in enumerate(polygons):
            item_id=f'{os.path.splitext(os.path.basename(file_path))[0]}_{idx}'
            item_id='geops_'+item_id
            # Create a STAC item for each polygon
            item = create_stac_item(file_path, polygon, bbox, start_time_value, psa_id, item_id)
            #add an asset
            thumbnail_path = "Mars_Viking_global.jpg"
            '''
            item.add_asset(
                "thumbnail",
                Asset(
                    href=os.path.relpath(thumbnail_path, output_dir),
                    media_type=MediaType.JPEG
                )
            )
            '''
            EOExtension.add_to(item)
            EOExtension.ext(item).bands = [Band.create(name=order)]
            # Add the item to the collection
            collection1.add_item(item)


folder_path = 'five_days_lno_v2'
output_dir='output_v2/'
nomad_stac_catalog = create_stac_collection(folder_path)
collec=nomad_stac_catalog.get_child('geops_10_days_lno_collection', recursive=True)
add_items(folder_path, collec, output_dir)

ncol=len(list(collec.get_all_collections()))
print(f"Number of orbits: {ncol}")

items = list(nomad_stac_catalog.get_items(recursive=True))
print(f"Total number of footprints: {len(items)}")
# Save the STAC catalog to a file
nomad_stac_catalog.normalize_hrefs(output_dir)
nomad_stac_catalog.save(catalog_type=CatalogType.SELF_CONTAINED, stac_io=MyCustomStacIo())

