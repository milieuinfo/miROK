import os
from qgis.core import QgsRasterLayer, QgsMapLayerRegistry
import mirok_tools as tools
# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================


mirokHome = os.environ['MIROK']


def run_indicator(selection, progress, info):
    progress.setValue(10)
    info.append("load WMS layer")
    url = "contextualWMSLegend=0&crs=EPSG:31370&dpiMode=7&featureCount=10&format=image/png&layers=0&transparent=true&styles=&url=http://inspirepub.waterinfo.be/arcgis/services/overstroombaargebied/MapServer/WmsServer"
    layer = QgsRasterLayer(url, "Overstroombaar gebied", "wms")
    tools.load_layer_in_group(layer)
    progress.setValue(100)
