import json
import pystac
import datetime
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.file import FileExtension
import hashlib
import fsspec

# creation de l'item
item_datetime = datetime.datetime(2023, 9, 10, 12, 0, 0)  # Par exemple, le 10 septembre 2023 à 12:00:00
item = pystac.Item(
    id="example-item",
    geometry=None,
    bbox=None,
    datetime=item_datetime,
    properties={}
)


# creation de la ressource Asset
pdf_path = "doc_stac.pdf"
pdf_asset = pystac.Asset(
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
collection = pystac.Collection(
    id="example-collection",
    title="Exemple de Collection PySTAC",
    description="Ceci est une collection de données d'exemple en utilisant PySTAC.",
    license="CC-BY-SA",
    extent=pystac.Extent(
        spatial=pystac.SpatialExtent([-180, -90, 180, 90]),
        temporal=pystac.TemporalExtent([
            (datetime.datetime(2020, 1, 1), datetime.datetime(2021, 12, 31))
        ])
    )
)
collection.extra_fields['mission'] = "mission"
collection.extra_fields['platform'] = "platform"
collection.extra_fields['instruments'] = ["instrument"]
# Ajout de l'item à la collection
collection.add_item(item)
# Afficher la hiérarchisation
collection.describe()

import os
collection.normalize_hrefs(os.path.join("/tmp", "stac"))

{   "type": "Collection",
    "id": "example-collection",
    "stac_version": "1.0.0",
    "description": "Ceci est une collection de donn\u00e9es d'exemple en utilisant PySTAC.",
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

