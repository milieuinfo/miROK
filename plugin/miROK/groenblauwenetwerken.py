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
prj = mirokHome + "\\5groenblauweNetwerken"


def run_indicator(input_file, wegen, spoor, water, waterlopen, selection, progress_bar, info, save_default):
    progress_bar.setValue(10)

    input_file = tools.handle_input_file(input_file, save_default, '5', "start", prj)

    info.append("load and recategorize raster")
    starting_array = tools.open_input_as_array(input_file)

    # BLAUW ============================================================================================================
    info.append("calculate indicator blauw netwerk")
    # recategorize raster
    # #WATER
    water_lu100m = np.select([
        (starting_array >= 35.9) & (starting_array <= 36.1)],
        [1], 0)

    # #SLIK en SCHORRE
    slik_schorre = np.select([
        (starting_array >= 28.9) & (starting_array <= 29.1)],
        [1], 0)
    progress_bar.setValue(20)

    # load water shapes and rasterize with gdx
    waterlopen = tools.handle_input_file(waterlopen, save_default, '5', "waterlopen", prj)

    # raster each shape catergory seperately to be able to combine it as different value on a raster.
    area = gdal.Open(mirokHome + "\\vlaanderen.tif").ReadAsArray()
    cat0 = tools.gdx_rasterized_shape_from_feature_as_array(waterlopen, "CATC", '0', area.shape)
    cat1 = tools.gdx_rasterized_shape_from_feature_as_array(waterlopen, "CATC", '1', area.shape)
    cat2 = tools.gdx_rasterized_shape_from_feature_as_array(waterlopen, "CATC", '2', area.shape)
    cat3 = tools.gdx_rasterized_shape_from_feature_as_array(waterlopen, "CATC", '3', area.shape)
    cat9 = tools.gdx_rasterized_shape_from_feature_as_array(waterlopen, "CATC", '9', area.shape)
    progress_bar.setValue(30)

    end_result = np.zeros_like(area)
    # combine different water rasters as different values
    end_result = np.where(end_result == 0, cat0 * 5, end_result)
    end_result = np.where(end_result == 0, cat1 * 4, end_result)
    end_result = np.where(end_result == 0, cat2 * 3, end_result)
    end_result = np.where(end_result == 0, cat3 * 2, end_result)
    end_result = np.where(end_result == 0, cat9 * 1, end_result)
    end_result = np.where(end_result == 0, slik_schorre * 6, end_result)
    end_result = np.where(end_result == 0, water_lu100m * 7, end_result)

    tools.save_array_as_tif_and_load_as_layer(prj + "\\blauwtype100m.tif", "Groenblauw netwerk: blauw", prj + "\\Legend5blauw.qml", end_result)

    # GROEN ===========================================================================================================
    info.append("calculate indicator Groen netwerk")

    wegen = tools.handle_input_file(wegen, save_default, '5', "wegen", prj)
    spoor = tools.handle_input_file(spoor, save_default, '5', "spoor", prj)
    water = tools.handle_input_file(water, save_default, '5', "water", prj)

    db_name = os.path.split(wegen)[1].split('.')[0]
    progress_bar.setValue(60)
    info.append("process ogr2ogr for transport layers")
    # note: main is expecting sys.argv, where the first argument is the script name
    # so, the argument indices in the array need to be offset by 1
    info.append("process wegen layer")
    ogr2ogr.main(["", "-f", "ESRI Shapefile", "-overwrite", prj + "\\inputWegen.shp", wegen, "-sql",
                  "SELECT * FROM " + db_name + " WHERE WEGCAT IN ('H','PI', 'PII', 'PII-2', 'PII-4', 'S', 'S1', 'S2', 'S3')"])
    info.append("process spoorwegen layer")
    ogr2ogr.main(["", "-f", "ESRI Shapefile", "-overwrite", prj + "\\inputSpoorwegen.shp", spoor])
    info.append("process waterwegen layer")
    ogr2ogr.main(["", "-f", "ESRI Shapefile", "-overwrite", prj + "\\inputWaterwegen.shp", water])
    progress_bar.setValue(70)

    # reclass
    groen_start = np.select([
        (starting_array >= 0) & (starting_array <= 1),
        (starting_array == 2),
        (starting_array >= 3) & (starting_array <= 5),
        (starting_array >= 6) & (starting_array <= 18),
        (starting_array == 19),
        (starting_array >= 20) & (starting_array <= 23),
        (starting_array >= 24) & (starting_array <= 29),
        (starting_array >= 30) & (starting_array <= 32),
        (starting_array >= 33) & (starting_array <= 34),
        (starting_array >= 35) & (starting_array <= 36)],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0])

    progress_bar.setValue(80)
    info.append("substract shapes from raster")
    # rasterize with gdx
    wegen = tools.rasterize_gdx_return_array(prj + '\\inputWegen.shp', groen_start.shape)
    spoor = tools.rasterize_gdx_return_array(prj + '\\inputSpoorwegen.shp', groen_start.shape)
    water = tools.rasterize_gdx_return_array(prj + '\\inputWaterwegen.shp', groen_start.shape)
    # subtract layers from groen_start
    groen_start = np.where(wegen == 1, 0, groen_start)
    groen_start = np.where(spoor == 1, 0, groen_start)
    groen_start = np.where(water == 1, 0, groen_start)

    progress_bar.setValue(85)
    info.append("clusterize and save")
    gdx_raster = tools.gdx_raster_from_array(groen_start)
    gdx_out = gdx.cluster_size(gdx_raster)
    gdx.write(gdx_out, prj + '\\groencluster.tif')

    info.append("load output layer")
    result = tools.load_mask_from_array(mirokHome + "\\vlaanderen.tif", tools.open_input_as_array(prj + '\\groencluster.tif'))
    tools.save_array_as_tif_and_load_as_layer(prj + '\\groencluster.tif', "Groenblauw netwerk: groen", prj + "\\Legend5groen.qml", result)

    progress_bar.setValue(90)
    end_result = gdal.Open(prj + "\\groencluster.tif").ReadAsArray()
    # normalize result for calculations
    end_result = np.select([
        (end_result > 1) & (end_result <= 10),
        (end_result > 10) & (end_result <= 100),
        (end_result > 100) & (end_result <= 1000),
        (end_result > 1000)],
        [2.5, 5, 7.5, 10], 0)
    tools.process_calculations_and_update_excel(end_result, selection, prj, '5_groenclusters', [2.5, 5, 7.5, 10])
    progress_bar.setValue(100)
