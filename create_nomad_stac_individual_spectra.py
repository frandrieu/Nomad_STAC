#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Oct 2023

Script to convert a NOMAD footprint into a STAC catalog

@author: fandrieu
"""

from pystac import Catalog, Item, Asset, MediaType, CatalogType, Collection, Extent, SpatialExtent, TemporalExtent, Provider, ProviderRole, Link, Summaries, RangeSummary
from datetime import datetime
import json
from pystac.extensions.file import FileExtension, ExtensionHooks
from shapely.geometry import mapping
import hashlib
import fsspec

from pystac.extensions.projection import ProjectionExtension
import os
import geopandas as gpd

def create_stac_item(file_path, polygon, bbox, start_time_value, item_id):
    # Create a STAC item for each polygon in the GeoJSON file
    #item_id = f'{os.path.splitext(os.path.basename(file_path))[0]}_{polygon.wkt}'  # Using polygon's WKT as part of the item ID
    #item = Item(id=item_id, geometry=polygon, bbox=bbox)

    # Convert start_time_value to ISO 8601 format using Python datetime library
    start_datetime_str = start_time_value.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if start_time_value else None
    #item.properties['start_datetime'] = start_datetime_str
    
   # Create a STAC item for each GeoJSON file
    item_datetime = start_time_value
    item = Item(
        id=item_id,
        geometry=mapping(polygon),
        bbox=list(bbox),
        datetime=item_datetime,
        properties={}
    )
    '''
    # creation de la ressource Asset
    pdf_path = "doc_stac.pdf"
    pdf_asset = Asset(
            href=pdf_path,
            media_type="application/pdf",
            title="Documentation",
            description="Documentation au format PDF",
            roles=["documentation"]
    )
     # ajout de la ressource à l'item
    item.add_asset("documentation", pdf_asset)
    # Utilisation de l'extension File sur l'asset
    pdf_asset_file = FileExtension.ext(pdf_asset, add_if_missing=True)
    md5_checksum = hashlib.md5(open(pdf_path, 'rb').read()).hexdigest()
    with fsspec.open(pdf_path) as file:
            pdf_asset_file.size = file.size
    pdf_asset_file.checkum = md5_checksum
    '''
    
    #item.common_metadata.title = "my title"
    #item.common_metadata.description = "my description"
    #item.common_metadata.platform = "my platform"
    #item.common_metadata.instruments = ["instru1"]
    #item.common_metadata.mission = "mission"
    #item.common_metadata.gsd = 10
    #item.common_metadata.created = item_datetime
    #item.common_metadata.updated = item_datetime
    # for the moment, we use that schema on because a fix must be set in the official repo
    item.stac_extensions.append('https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json')
    item.stac_extensions.append('https://stac-extensions.github.io/file/v2.1.0/schema.json')#)
    item.properties['ssys:targets'] = ['Mars']
    
    item.properties['processing:level']='footprint'
    
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



    '''
    # creation de la ressource Asset
    pdf_path = file_path
    item_asset = Asset(
            href=pdf_path,
            media_type='application/geo+json',
            title="File path",
            description={},
            roles=["path"]
    )
    
     # ajout de la ressource à l'item
    item.add_asset("File path", item_asset)
    '''
    
    #item.add_asset(key='geojson', href=file_path, media_type='application/geo+json')

    # Add the item to the catalog
    #item.set_self_href('item.json')
    #item.validate()
           
    
    #item.add_asset(key='geojson', href=file_path, media_type='application/geo+json')

    return item

def get_geojson_info(file_path):
    # Read GeoJSON file using geopandas
    gdf = gpd.read_file(file_path)

    # Extract bounding box (bbox) boundaries
    bbox = gdf.total_bounds

    # Extract start_time from GeoJSON file (assuming it's in a 'start_time' property)
    start_time_str = gdf.iloc[0].get('start_time', None)

    # Parse start_time string to datetime object
    start_time_value = datetime.strptime(start_time_str, '%Y %b %d %H:%M:%S.%f') if start_time_str else None

    # Extract polygons
    polygons = gdf.geometry.tolist()

    return polygons, bbox, start_time_value



'''
def get_geojson_files(folder_path):
    # Get the list of files in the specified folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".geojson")]

    all_polygons = []
    all_bboxes = []
    all_datetime = []

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        polygons, bbox = get_geojson_info(file_path)

        # Append to the lists
        all_polygons.extend(polygons)
        all_bboxes.append(bbox)

    
        # Print information or perform further processing
        print(f"File: {file_path}")
    
    return all_polygons, all_bboxes, all_datetime
'''

def create_stac_collection(folder_path, catalog_title='5 day Nomad Collection'):
   # Create a STAC catalog
   
   
    # Example collection creation
    nomad_collection = Collection(
        id="5 days lno - collection",
        title="5 days lno - PySTAC prototype",
        description="Collection of 5 days of NOMAD data to make a STAC prototype",
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
    
    #OUTPUT = 'STAC_footprints/'
    #DATA = 'footprints/'
    #WEBSITE = 'tbd'
    #DEBUG = True
    
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
        'processing:level': 'footprint',
        
    }
    
    CATALOG = Catalog(
        id='nomad-lno',
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
            
    ])
    
    
    #nomad_collection.normalize_hrefs(os.path.join("/tmp", "stac"))
    CATALOG.add_child(nomad_collection)
    
    # Get the list of files in the specified folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".geojson")]

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        polygons, bbox, start_time_value = get_geojson_info(file_path)
        
        # Parse start_time string to datetime object
        #start_time_value = datetime.strptime(start_time_str, '%Y %b %d %H:%M:%S.%f') if start_time_str else None
        for idx, polygon in enumerate(polygons):
            item_id=f'{os.path.splitext(os.path.basename(file_path))[0]}_{idx}'
            # Create a STAC item for each polygon
            item = create_stac_item(file_path, polygon, bbox, start_time_value, item_id)
            
            # Add the item to the catalog
            #catalog.add_item(item)
            nomad_collection.add_item(item)
    #nomad_collection.set_self_href('_nomad_collection.json')
    
                                 
    #nomad_collection.normalize_hrefs(os.path.join("/tmp", "stac"@))
    
    return CATALOG


folder_path = 'five_days_lno'
nomad_stac_catalog = create_stac_collection(folder_path)


# Save the STAC catalog to a file
nomad_stac_catalog.normalize_and_save(root_href='output/',catalog_type=CatalogType.SELF_CONTAINED)
nomad_stac_catalog.normalize_hrefs('output/')
nomad_stac_catalog.save(catalog_type=CatalogType.SELF_CONTAINED )

items = list(nomad_stac_catalog.get_items(recursive=True))

print(f"Number of items: {len(items)}")
#for item in items:
#    print(f"- {item.id}")
    
# Clean the export folder

# Normilize hrefs

#nomad_stac_catalog.describe()
#collec=nomad_stac_catalog.get_child(id='5 days lno - collection')
#print(json.dumps(collec.to_dict(), indent=4))
#nomad_stac_catalog.save(catalog_type=CatalogType.SELF_CONTAINED)
'''

# creation de l'item
item_datetime = datetime.datetime(2023, 9, 10, 12, 0, 0)  # Par exemple, le 10 septembre 2023 à 12:00:00
item = Item(
    id="example-item",
    geometry=None,
    bbox=None,
    datetime=item_datetime,
    properties={}
)


# creation de la ressource Asset
pdf_path = "doc_stac.pdf"
pdf_asset = Asset(
        href=pdf_path,
        media_type="application/pdf",
        title="Documentation",
        description="Documentation au format PDF",
        roles=["documentation"]
)
 # ajout de la ressource à l'item
item.add_asset("documentation", pdf_asset)
# Utilisation de l'extension File sur l'asset
pdf_asset_file = FileExtension.ext(pdf_asset, add_if_missing=True)
md5_checksum = hashlib.md5(open(pdf_path, 'rb').read()).hexdigest()
with fsspec.open(pdf_path) as file:
        pdf_asset_file.size = file.size
pdf_asset_file.checkum = md5_checksum


item.common_metadata.title = "my title"
item.common_metadata.description = "my description"
item.common_metadata.platform = "my platform"
item.common_metadata.instruments = ["instru1"]
item.common_metadata.mission = "mission"
item.common_metadata.gsd = 10
item.common_metadata.created = item_datetime
item.common_metadata.updated = item_datetime
# for the moment, we use that schema on because a fix must be set in the official repo
item.stac_extensions.append('https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json')
item.properties['ssys:targets'] = ['Mars']

item.properties['processing:level']='Raw'

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


# création de la collection
nomad_collection = Collection(
    id="example-collection",
    title="Exemple de Collection PySTAC",
    description="Ceci est une collection de données d'exemple en utilisant ",
    license="CC-BY-SA",
    extent=Extent(
        spatial=SpatialExtent([-180, -90, 180, 90]),
        temporal=TemporalExtent([
            (datetime.datetime(2020, 1, 1), datetime.datetime(2021, 12, 31))
        ])
    )
)
nomad_collection.extra_fields['mission'] = "mission"
nomad_collection.extra_fields['platform'] = "platform"
nomad_collection.extra_fields['instruments'] = ["instrument"]
# Ajout de l'item à la collection
nomad_collection.add_item(item)
# Afficher la hiérarchisation
nomad_collection.describe()

import os
nomad_collection.normalize_hrefs(os.path.join("/tmp", "stac"))

{   "type": "Collection",
    "id": "example-collection",
    "stac_version": "1.0.0",
    "description": "Ceci est une collection de donn\u00e9es d'exemple en utilisant ",
    "links": [
        {
            "rel": "root",
            "href": "/tmp/stac/collection.json",
            "type": "application/json",
            "title": "Exemple de Collection PySTAC"
        },
        {
            "rel": "item",
            "href": "/tmp/stac/example-item/example-item.json",
            "type": "application/json"
        },
        {
            "rel": "self",
            "href": "/tmp/stac/collection.json",    
            "type": "application/json"
        }
    ],
    "title": "Exemple de Collection PySTAC",
        "mission": "mission",
        "platform": "platform",
        "instruments": "instruments",
    "extent": {
        "spatial": {
        "bbox": [
            -180,
            -90, 
            180, 
            90
            ] 
        },
        "temporal": {
            "interval": [
                [
                    "2020-01-01T00:00:00Z",
                    "2021-12-31T00:00:00Z"
                ] 
            ]
        }
    },
   "license": "CC-BY-SA" 
 }
print(json.dumps(item.to_dict(), indent=4))


#### Loading footprint

#### Catalog metadata

OUTPUT = 'STAC_footprints/'
DATA = 'footprints/'
WEBSITE = 'tbd'
DEBUG = True

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
    'processing:level': 'footprint',
    
}

CATALOG = Catalog(
    id='nomad-lno',
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
        #'ssys:targets': sorted(SATELLITES_FLYBYS.keys()),
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
        
])


item_datetime = datetime.datetime(2023, 9, 10, 12, 0, 0)  # Par exemple, le 10 septembre 2023 à 12:00:00
item = Item(
        id="example-item",
        geometry=None,
        bbox=None,
        datetime=item_datetime,
        properties={}
)

CATALOG.add_child(nomad_collection)


nomad_collection
'''