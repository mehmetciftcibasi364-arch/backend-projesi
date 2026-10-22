import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")
def get_access_token():

    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    return response.json()["access_token"]
def get_ndvi(latitude: float, longitude: float):
    token = get_access_token()

    url = "https://sh.dataspace.copernicus.eu/statistics/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    delta = 0.001

    bbox = [
        longitude - delta,
        latitude - delta,
        longitude + delta,
        latitude + delta
    ]
    evalscript = """
        //VERSION=3

    function setup() {
        return {
            input: ["B04", "B08", "dataMask"],
            output: [
                {
                    id: "ndvi",
                    bands: 1,
                    sampleType: "FLOAT32"
                },
                {
                    id: "dataMask",
                    bands: 1
                }
            ]
        };
    }

    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);

        return {
            ndvi: [ndvi],
            dataMask: [sample.dataMask]
        };
    }
    """
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "mosaickingOrder": "leastCC"
                    }
                }
            ]
        },
        "aggregation": {
            "timeRange": {
                "from": "2026-10-01T00:00:00Z",
                "to": "2026-10-23T00:00:00Z"
            },
            "aggregationInterval": {
                "of": "P22D"
            },
            "evalscript": evalscript,
            "resx": 10,
            "resy": 10
        }
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    return response.json()
    
def get_sentinel_data(latitude: float, longitude: float):
    result = get_ndvi(latitude, longitude)
    ndvi = result["data"][0]["outputs"]["ndvi"]["bands"]["B0"]["stats"]["mean"]
    if ndvi >= 0.6:
        vegetation_status = "İyi"
    elif ndvi >= 0.3:
        vegetation_status = "Orta"
    else:
        vegetation_status = "Düşük"
    """
    Sentinel uydu verisi için hazırlık katmanı.
    Şimdilik konuma göre standart bir veri yapısı döndürür.
    Sonraki aşamada gerçek Sentinel-1/2 servisine bağlanacaktır.
    """

    return {
        "status": "success",
        "source": "Sentinel-2",
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "satellite_data": {
            "ndvi": round(ndvi, 3),
            "vegetation_status": vegetation_status
        }
    }

def get_sentinel1_data(latitude: float, longitude: float):
    token = get_access_token()

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    delta = 0.001

    bbox = [
        longitude - delta,
        latitude - delta,
        longitude + delta,
        latitude + delta
    ]
    evalscript = """
    //VERSION=3

    function setup() {
        return {
            input: ["VV", "VH", "dataMask"],
            output: {
                bands: 3,
                sampleType: "FLOAT32"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.VV, sample.VH, sample.dataMask];
    }
    """
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox
            },
            "data": [
                {
                    "type": "sentinel-1-grd",
                    "dataFilter": {
                        "polarization": "DV"
                    }
                }
            ]
        },
        "output": {
            "width": 1,
            "height": 1,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },
        "evalscript": evalscript
    
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    return response.content