import os
import mirok_tools as tools
import numpy as np
import ogr2ogr
from osgeo import gdal
import gdx
# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================
mirokHome = os.environ['MIROK']
prj = mirokHome + "\\4openRuimte"


def run_indicator(input_file, wegen, spoor, water, selection, progress_bar, info,save_default):
    progress_bar.setValue(10)
    wegen = tools.handle_input_file(wegen, save_default, '4', "wegen", prj)
    spoor = tools.handle_input_file(spoor, save_default, '4', "spoor", prj)
    water = tools.handle_input_file(water, save_default, '4', "water", prj)

    db_name = os.path.split(wegen)[1].split('.')[0]

    info.append("process ogr2ogr for transport layers")
    # note: main is expecting sys.argv, where the first argument is the script name
    # so, the argument indices in the array need to be offset by 1
    info.append("process wegen layer")
    ogr2ogr.main(["", "-f", "ESRI Shapefile", "-overwrite", prj + "\inputWegen.shp", wegen, "-sql",
                  "SELECT * FROM " + db_name + " WHERE WEGCAT IN ('H','PI', 'PII', 'PII-2', 'PII-4', 'S', 'S1', 'S2', 'S3')"])
    progress_bar.setValue(20)
    info.append("process spoorwegen layer")
    ogr2ogr.main(["", "-f", "ESRI Shapefile", "-overwrite", prj + "\inputSpoorwegen.shp", spoor])
    progress_bar.setValue(30)
    info.append("process waterwegen layer")
    ogr2ogr.main(["", "-f", "ESRI Shapefile", "-overwrite", prj + "\inputWaterwegen.shp", water])
    progress_bar.setValue(40)

    info.append("load and recategorize raster")

    input_file = tools.handle_input_file(input_file, save_default, '4', "start", prj)

    open_ruimte = tools.open_input_as_array(input_file)

    # recategorize raster
    open_ruimte = np.select([
        (open_ruimte >= 0) & (open_ruimte <= 5),
        (open_ruimte >= 18) & (open_ruimte <= 30),
        (open_ruimte >= 33) & (open_ruimte <= 34),
        (open_ruimte == 36)],
        [1, 1, 1, 1], 0)

    info.append("substract shapes from raster")
    # rasterize with gdx
    wegen = tools.rasterize_gdx_return_array(prj + '\\inputWegen.shp', open_ruimte.shape)
    spoor = tools.rasterize_gdx_return_array(prj + '\\inputSpoorwegen.shp', open_ruimte.shape)
    water = tools.rasterize_gdx_return_array(prj + '\\inputWaterwegen.shp', open_ruimte.shape)
    # subtract layers from open_ruimte
    open_ruimte = np.where(wegen == 1, 0, open_ruimte)
    open_ruimte = np.where(spoor == 1, 0, open_ruimte)
    open_ruimte = np.where(water == 1, 0, open_ruimte)
    tools.load_mask_from_array(mirokHome + "\\vlaanderen.tif",open_ruimte)
    progress_bar.setValue(50)
    info.append("clusterize and save")
    gdx_raster = tools.gdx_raster_from_array(open_ruimte)
    gdx_out = gdx.cluster_size(gdx_raster)
    gdx.write(gdx_out, prj + '\\open_ruimte.tif')

    info.append("load output layer")
    result = tools.load_mask_from_array(mirokHome + "\\vlaanderen.tif",tools.open_input_as_array(prj + '\\open_ruimte.tif'))
    tools.save_array_as_tif_and_load_as_layer(prj + '\\open_ruimte.tif',"Open ruimte",  prj + "\\legend4.qml", result)

    progress_bar.setValue(60)

    result_array100m = tools.open_input_as_array(prj + '\\open_ruimte.tif')
    progress_bar.setValue(80)
    #normalize result for calculations
    result_array100m = np.select([
        (result_array100m > 1) & (result_array100m <= 10),
        (result_array100m > 10) & (result_array100m <= 100),
        (result_array100m > 100) & (result_array100m <= 1000),
        (result_array100m > 1000)],
        [2.5, 5, 7.5, 10], 0)

    tools.process_calculations_and_update_excel(result_array100m, selection, prj, '4_open_ruimte',[2.5, 5, 7.5, 10])
    progress_bar.setValue(100)
