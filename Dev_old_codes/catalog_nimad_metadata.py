#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Oct 2023

Script to convert a NOMAD footprint into a STAC catalog

@author: fandrieu
"""

from pystac import Catalog, Item, Asset, MediaType, CatalogType, Collection, Extent, SpatialExtent, TemporalExtent, Provider, ProviderRole, Link, Summaries, RangeSummary

import json
import pystac
from pystac.extensions.file import FileExtension
import hashlib
import fsspec
import datetime

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
item = pystac.Item(
        id="example-item",
        geometry=None,
        bbox=None,
        datetime=item_datetime,
        properties={}
)


