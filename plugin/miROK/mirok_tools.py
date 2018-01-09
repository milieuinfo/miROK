import csv
import os
import time
import numpy as np
import numspataggr
import win32com.client as win32
from osgeo import gdal, ogr, osr
from osgeo.gdalnumeric import BandWriteArray
from qgis.core import QgsMapLayerRegistry, QgsProject, QgsRasterLayer, QgsFillSymbolV2, \
    QgsSingleBandGrayRenderer, QgsContrastEnhancement, QgsRasterBandStats, QgsCoordinateReferenceSystem
from qgis.utils import iface
import gdx
import shutil
from PyQt4.QtCore import QTimer

mirokHome = os.environ['MIROK']


def mean_or_na(a):
    if np.isnan(a).all():
        return "#N/A"
    else:
        return format(np.nanmean(a, dtype=np.float32), '.4f')


# burn selected shape file to a raster with value 1 inside the shape. Make shape transparent
def process_selection(starting_array100m, selection_file, prj, cell_size=100):
    if selection_file is not None:
        source_ds = ogr.Open(selection_file)
        source_layer = source_ds.GetLayer()

        raster = gdal.GetDriverByName('GTiff').Create(prj + "\\selection.tif", int(237000 / cell_size), int(92000 / cell_size), 1, gdal.GDT_Byte)
        raster.SetGeoTransform((22000.0, cell_size, 0.0, 245000.0, 0.0, -cell_size))
        band = raster.GetRasterBand(1)
        band.SetNoDataValue(np.NaN)

        # Rasterize, burn selection to value 1
        gdal.RasterizeLayer(raster, [1], source_layer, burn_values=[1])
        selection = raster.ReadAsArray()
        raster = None
        # make fill transparent of selection layer
        for selection_layer in iface.legendInterface().layers():
            if selection_layer.name() == source_layer.GetName():
                my_renderer = selection_layer.rendererV2()
                my_symbol1 = QgsFillSymbolV2.createSimple(
                    {'color': '0,0,0,0', 'color_border': '#000000', 'width_border': '0.6'})
                my_renderer.setSymbol(my_symbol1)
                selection_layer.triggerRepaint()
        # mask startingArray with the selection, set rest to NaN
        del source_ds, source_layer, raster, band
        return np.where(selection == 1, starting_array100m, np.NaN), selection


# calculate and save values into excel file
def calculate_and_save_indicators(starting_array100m, vlaanderen_array, sheet_name, selection, selection_file=None, legend=None, cell_size=100):
    # load mask raster maps into arrays
    if cell_size == 100:
        bevolking = gdal.Open(mirokHome + "\\gebiedstypering_volgens_bevolking123.tif").ReadAsArray()
        bebouwing = gdal.Open(mirokHome + "\\gebiedstypering_volgens_bebouwing123.tif").ReadAsArray()
        voorziening = gdal.Open(mirokHome + "\\gebiedstypering_volgens_voorzieningen123.tif").ReadAsArray()
    if cell_size == 10:
        bevolking = gdal.Open(mirokHome + "\\gebiedstypering_volgens_bevolking123_10m.tif").ReadAsArray()
        bevolking = bevolking.astype(np.int8)
        bebouwing = gdal.Open(mirokHome + "\\gebiedstypering_volgens_bebouwing123_10m.tif").ReadAsArray()
        bebouwing = bebouwing.astype(np.int8)
        voorziening = gdal.Open(mirokHome + "\\gebiedstypering_volgens_voorzieningen123_10m.tif").ReadAsArray()
        voorziening = voorziening.astype(np.int8)
    if cell_size == 10:
        factor = 10000
        vlaanderen = gdal.Open(mirokHome + "\\vlaanderen_10m.tif").ReadAsArray()
    if cell_size == 100:
        factor = 100
        vlaanderen = gdal.Open(mirokHome + "\\vlaanderen.tif").ReadAsArray()
    if selection is None:
        selection = vlaanderen
    area_selection = np.nansum(np.where(selection == 1, 1, 0), dtype=np.float32) / factor
    valid_selection = selection > 0
    area_bevolking_landelijk = np.nansum(np.where(bevolking == 1, valid_selection, 0), dtype=np.float32) / factor
    area_bevolking_rand = np.nansum(np.where(bevolking == 2, valid_selection, 0), dtype=np.float32) / factor
    area_bevolking_stedelijk = np.nansum(np.where(bevolking == 3, valid_selection, 0), dtype=np.float32) / factor
    area_bebouwing_landelijk = np.nansum(np.where(bebouwing == 1, valid_selection, 0), dtype=np.float32) / factor
    area_bebouwing_rand = np.nansum(np.where(bebouwing == 2, valid_selection, 0), dtype=np.float32) / factor
    area_bebouwing_stedelijk = np.nansum(np.where(bebouwing == 3, valid_selection, 0), dtype=np.float32) / factor
    area_voorziening_landelijk = np.nansum(np.where(voorziening == 1, valid_selection, 0), dtype=np.float32) / factor
    area_voorziening_rand = np.nansum(np.where(voorziening == 2, valid_selection, 0), dtype=np.float32) / factor
    area_voorziening_stedelijk = np.nansum(np.where(voorziening == 3, valid_selection, 0), dtype=np.float32) / factor
    del valid_selection
    # vlaanderen
    area_selection_vl = np.nansum(np.where(vlaanderen == 1, 1, 0), dtype=np.float32) / factor
    valid_vl = vlaanderen > 0
    area_bevolking_landelijk_vl = np.nansum(np.where(bevolking == 1, valid_vl, 0), dtype=np.float32) / factor
    area_bevolking_rand_vl = np.nansum(np.where(bevolking == 2, valid_vl, 0), dtype=np.float32) / factor
    area_bevolking_stedelijk_vl = np.nansum(np.where(bevolking == 3, valid_vl, 0), dtype=np.float32) / factor
    area_bebouwing_landelijk_vl = np.nansum(np.where(bebouwing == 1, valid_vl, 0), dtype=np.float32) / factor
    area_bebouwing_rand_vl = np.nansum(np.where(bebouwing == 2, valid_vl, 0), dtype=np.float32) / factor
    area_bebouwing_stedelijk_vl = np.nansum(np.where(bebouwing == 3, valid_vl, 0), dtype=np.float32) / factor
    area_voorziening_landelijk_vl = np.nansum(np.where(voorziening == 1, valid_vl, 0), dtype=np.float32) / factor
    area_voorziening_rand_vl = np.nansum(np.where(voorziening == 2, valid_vl, 0), dtype=np.float32) / factor
    area_voorziening_stedelijk_vl = np.nansum(np.where(voorziening == 3, valid_vl, 0), dtype=np.float32) / factor
    del valid_vl, vlaanderen
    try:
        excel = win32.client.GetActiveObject("Excel.Application")
        print("Running Excel instance found, returning object")

    except:
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = False
        print("No running Excel instances, returning new instance")

    # open excel file
    wb = excel.Workbooks.Open(mirokHome + '\\gebiedstype_analyse_results.xlsx')
    ws = wb.Sheets(sheet_name)
    # update mean values
    ws.Cells(4, 9).Value = mean_or_na(np.where(bevolking == 1, starting_array100m, np.NaN))
    ws.Cells(5, 9).Value = mean_or_na(np.where(bevolking == 2, starting_array100m, np.NaN))
    ws.Cells(6, 9).Value = mean_or_na(np.where(bevolking == 3, starting_array100m, np.NaN))
    ws.Cells(4, 13).Value = mean_or_na(np.where(bevolking == 1, vlaanderen_array, np.NaN))
    ws.Cells(5, 13).Value = mean_or_na(np.where(bevolking == 2, vlaanderen_array, np.NaN))
    ws.Cells(6, 13).Value = mean_or_na(np.where(bevolking == 3, vlaanderen_array, np.NaN))
    del bevolking
    ws.Cells(10, 9).Value = mean_or_na(np.where(bebouwing == 1, starting_array100m, np.NaN))
    ws.Cells(11, 9).Value = mean_or_na(np.where(bebouwing == 2, starting_array100m, np.NaN))
    ws.Cells(12, 9).Value = mean_or_na(np.where(bebouwing == 3, starting_array100m, np.NaN))
    ws.Cells(10, 13).Value = mean_or_na(np.where(bebouwing == 1, vlaanderen_array, np.NaN))
    ws.Cells(11, 13).Value = mean_or_na(np.where(bebouwing == 2, vlaanderen_array, np.NaN))
    ws.Cells(12, 13).Value = mean_or_na(np.where(bebouwing == 3, vlaanderen_array, np.NaN))
    del bebouwing
    ws.Cells(16, 9).Value = mean_or_na(np.where(voorziening == 1, starting_array100m, np.NaN))
    ws.Cells(17, 9).Value = mean_or_na(np.where(voorziening == 2, starting_array100m, np.NaN))
    ws.Cells(18, 9).Value = mean_or_na(np.where(voorziening == 3, starting_array100m, np.NaN))
    ws.Cells(16, 13).Value = mean_or_na(np.where(voorziening == 1, vlaanderen_array, np.NaN))
    ws.Cells(17, 13).Value = mean_or_na(np.where(voorziening == 2, vlaanderen_array, np.NaN))
    ws.Cells(18, 13).Value = mean_or_na(np.where(voorziening == 3, vlaanderen_array, np.NaN))
    del voorziening
    ws.Cells(20, 2).Value = mean_or_na(vlaanderen_array)  # mean of vlaanderen
    ws.Cells(21, 2).Value = mean_or_na(starting_array100m)  # mean of selection
    del vlaanderen_array
    # surface area per legend section
    if legend:
        had_zero = False
        from_val = 0
        for idx, val in enumerate(legend):
            if val < 0:
                ws.Cells(23 + idx, 3).Value = np.nansum(np.where(selection == 1, np.isnan(starting_array100m), 0), dtype=np.float32) / factor
            elif val == 0:
                ws.Cells(23 + idx, 3).Value = np.nansum(np.where((starting_array100m == val), ~np.isnan(starting_array100m), 0), dtype=np.float32) / factor
                had_zero = True
            else:
                if had_zero:
                    ws.Cells(23 + idx, 3).Value = np.nansum(np.where((starting_array100m > from_val) & (starting_array100m < val), ~np.isnan(starting_array100m), 0),
                                                            dtype=np.float32) / factor
                    had_zero = False
                else:
                    ws.Cells(23 + idx, 3).Value = np.nansum(
                        np.where((starting_array100m >= from_val) & (starting_array100m < val), ~np.isnan(starting_array100m), 0),
                        dtype=np.float32) / factor
            from_val = max(val, from_val)
        ws.Cells(23 + len(legend), 3).Value = np.nansum(np.where(starting_array100m >= from_val, ~np.isnan(starting_array100m), 0), dtype=np.float32) / factor

    wss = wb.Sheets("selectie")
    if selection_file:
        wss.Cells(2, 1).Value = os.path.basename(selection_file).split('.')[0]

    wss.Cells(1, 2).Value = area_selection
    wss.Cells(5, 2).Value = area_bevolking_landelijk
    wss.Cells(5, 3).Value = area_bevolking_rand
    wss.Cells(5, 4).Value = area_bevolking_stedelijk
    wss.Cells(6, 2).Value = area_bebouwing_landelijk
    wss.Cells(6, 3).Value = area_bebouwing_rand
    wss.Cells(6, 4).Value = area_bebouwing_stedelijk
    wss.Cells(7, 2).Value = area_voorziening_landelijk
    wss.Cells(7, 3).Value = area_voorziening_rand
    wss.Cells(7, 4).Value = area_voorziening_stedelijk
    # vlaanderen
    wss.Cells(1, 6).Value = area_selection_vl
    wss.Cells(5, 6).Value = area_bevolking_landelijk_vl
    wss.Cells(5, 7).Value = area_bevolking_rand_vl
    wss.Cells(5, 8).Value = area_bevolking_stedelijk_vl
    wss.Cells(6, 6).Value = area_bebouwing_landelijk_vl
    wss.Cells(6, 7).Value = area_bebouwing_rand_vl
    wss.Cells(6, 8).Value = area_bebouwing_stedelijk_vl
    wss.Cells(7, 6).Value = area_voorziening_landelijk_vl
    wss.Cells(7, 7).Value = area_voorziening_rand_vl
    wss.Cells(7, 8).Value = area_voorziening_stedelijk_vl
    wb.Save()
    wb.Close()
    excel.Application.Quit()


# get a ndarray of a rasterized shape, rasterized by gdx
def rasterize_gdx_return_array(input_shape, output_shape_tuple):
    gdx_raster = gdx_raster_from_array(np.zeros((output_shape_tuple[0], output_shape_tuple[1])))
    gdx.draw_shape_on_raster(gdx_raster, input_shape.decode('utf-8'))
    return gdx_raster.ndarray


# open raster or shape as numpy array. conversion to correct size is done. result is always 920*2370 with a clip of vlaanderen
def open_input_as_array(input_file, bintype="sum", shape_attribute="value", cell_size=100):
    gdal.UseExceptions()
    if input_file.endswith(".shp") or input_file.endswith(".gpkg"):
        # input is Vector
        starting_map = rasterize_shape(input_file, shape_attribute, cell_size)
    else:
        starting_map = gdal.Open(input_file)

    if not ((starting_map.RasterXSize == 2370 or starting_map.RasterXSize == 23700) and (
                    starting_map.RasterYSize == 920 or starting_map.RasterYSize == 9200)):
        # input has wrong bounds, warp to correct ones
        gt = starting_map.GetGeoTransform()
        t = time.time()
        starting_map = gdal.Warp('', starting_map, format='MEM', xRes=gt[1], yRes=-gt[5], resampleAlg=gdal.GRA_NearestNeighbour, errorThreshold=0.0, multithread=True,
                                 outputBounds=[22000.0, 153000.0, 259000.0, 245000.0], outputType=gdal.GDT_Float32)
        print("w " + str(time.time() - t))
    gt = starting_map.GetGeoTransform()
    # cell size == 10
    if cell_size == 100 and gt[1] == 10 and -gt[5] == 10 and starting_map.RasterXSize == 23700 and starting_map.RasterYSize == 9200:
        # input has 10m cell size, numspataggr to 100m
        t = time.time()
        starting_array = read_as_array_without_noData(starting_map).astype(np.float32)
        starting_array100m = numspataggr.rebin(starting_array,
                                               (starting_array.shape[0] / 10, starting_array.shape[1] / 10), bintype)

        del starting_array
        if bintype == "sum":
            # rescale values added by numspataggr for calculations
            starting_array100m = starting_array100m / 100
        print(time.time() - t)
    elif cell_size == 100 and not (starting_map.RasterXSize == 2370 and starting_map.RasterYSize == 920):
        # input has incorrect size, translate to correct size
        starting_map = gdal.Translate('', starting_map, format='MEM', width=2370, height=920)
        starting_array100m = read_as_array_without_noData(starting_map)
    else:
        starting_array100m = read_as_array_without_noData(starting_map)
    # clip vlaanderen from all maps
    if cell_size == 100:
        vlaanderen = gdal.Open(mirokHome + "\\vlaanderen.tif").ReadAsArray()
        starting_array100m = np.where(vlaanderen == 1, starting_array100m, np.NaN)
        del vlaanderen
    del starting_map, gt
    return starting_array100m


def read_as_array_without_noData(starting_map):
    starting_array100m = starting_map.ReadAsArray()
    band = starting_map.GetRasterBand(1)
    no_data = band.GetNoDataValue()
    # set all noData points to NaN for calculations
    if no_data in starting_array100m:
        print("nan")
        starting_array100m = np.where(starting_array100m == no_data, np.NaN, starting_array100m)
    del band, no_data
    return starting_array100m


def rasterize_shape(input_file, shape_attribute, cell_size=100, no_data=np.NaN):
    raster = gdal.GetDriverByName('MEM').Create("", 237000 / cell_size, 92000 / cell_size, 1, gdal.GDT_Byte)
    raster.SetGeoTransform((22000.0, cell_size, 0.0, 245000.0, 0.0, -cell_size))
    source_ds = ogr.Open(input_file)
    source_layer = source_ds.GetLayer()
    band = raster.GetRasterBand(1)
    band.SetNoDataValue(no_data)
    if has_layer_attribute(source_layer, shape_attribute):
        # if attribute is present, use it as raster value.
        gdal.RasterizeLayer(raster, [1], source_layer, options=["ATTRIBUTE=" + shape_attribute])
    else:
        # else burn shape to raster with '1' as value
        gdal.RasterizeLayer(raster, [1], source_layer, burn_values=[1])
    del source_ds, source_layer, band
    return raster


def has_layer_attribute(source_layer, value):
    ldefn = source_layer.GetLayerDefn()
    for n in range(ldefn.GetFieldCount()):
        fdefn = ldefn.GetFieldDefn(n)
        if fdefn.name == value:
            return True
    return False


# load a file as a layer into qgis. optional legend file can be provided
def load_layer(file_name, layer_name, legend, force_crs=False):
    layer = QgsRasterLayer(file_name, layer_name)
    if force_crs:
        CRS = QgsCoordinateReferenceSystem()
        CRS.createFromSrid(31370)  #
        layer.setCrs(CRS)
    if legend is not None:  # load custom legend
        layer.loadNamedStyle(legend)
        layer.triggerRepaint()
    else:  # generate legend with min/max values
        renderer = QgsSingleBandGrayRenderer(layer.dataProvider(), 1)
        ce = QgsContrastEnhancement(layer.dataProvider().dataType(0))
        ce.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
        stats = layer.dataProvider().bandStatistics(1, QgsRasterBandStats.All, layer.extent())
        ce.setMinimumValue(stats.minimumValue)
        ce.setMaximumValue(stats.maximumValue)
        renderer.setContrastEnhancement(ce)
        layer.setRenderer(renderer)
    load_layer_in_group(layer)


def load_layer_in_group(layer):
    root = QgsProject.instance().layerTreeRoot()
    mygroup = root.findGroup("run")
    if mygroup:
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        mygroup.addLayer(layer)
    else:
        QgsMapLayerRegistry.instance().addMapLayer(layer)
    layer.triggerRepaint()


def save_array_as_tif_and_load_as_layer(file_name, layer_name, legend, array_to_save, cell_size=100):
    file_name = file_name.split(".")
    file_name = file_name[0] + str(int(round(time.time() * 1000))) + "." + file_name[1]
    save_array_as_tif(file_name, array_to_save, cell_size=cell_size)
    load_layer(file_name, layer_name, legend)


# save a numpy array as a GTiff file with gdal
def save_array_as_tif(output_path_name, array_to_save, cell_size=100):
    gdal.UseExceptions()
    driver = gdal.GetDriverByName("GTiff")
    shape = array_to_save.shape

    ds_out = driver.Create(output_path_name, shape[1], shape[0], 1, gdal.GDT_Float32, options=['COMPRESS=LZW'])

    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromEPSG(31370)
    ds_out.SetProjection(raster_srs.ExportToWkt())
    if cell_size == 100:
        array_to_save = load_mask_from_array(mirokHome + "\\vlaanderen.tif", array_to_save)
    # set cell size to 100*100
    ds_out.SetGeoTransform((22000.0, cell_size, 0.0, 245000.0, 0.0, -cell_size))
    band_out = ds_out.GetRasterBand(1)
    band_out.SetNoDataValue(np.NaN)
    BandWriteArray(band_out, array_to_save.astype("float32"))
    band_out.ComputeStatistics(0)
    del driver, ds_out, band_out


# combine a mask array with a array
def load_mask_from_array(mask_file, array):
    mask = gdal.Open(mask_file).ReadAsArray()
    return np.where(mask == 1, array, np.NaN)


def handle_input_file(input_file, save_default, indicator, file_type, prj):
    if input_file is None:
        file_name = load_default_filename(indicator, file_type)
        if file_name.startswith('\\'):
            input_file = prj + file_name
        else:
            input_file = file_name
    elif save_default:
        save_default_filename(indicator, file_type, input_file)
    return input_file


# load filename from txt file for defaults
def load_default_filename(indicator, subtype):
    csv_file = csv.reader(open(mirokHome + "\\default_files.txt", "rb"), delimiter=",")
    for row in csv_file:
        if indicator == row[0]:
            for item in row:
                if item.split('$')[0] == subtype:
                    return item.split('$')[1]


def save_default_filename(indicator, subtype, new_file):
    with open(mirokHome + "\\default_files.txt", 'rb') as csvfile, open(mirokHome + "\\outputfile.txt", 'wb') as output:
        reader = csv.reader(csvfile, delimiter=",")
        writer = csv.writer(output, delimiter=",")
        for row in reader:
            if indicator == row[0]:
                newrow = row[:]
                for index, item in enumerate(newrow):
                    if item.split('$')[0] == subtype:
                        newrow[index] = subtype + '$' + new_file
                writer.writerow(newrow)
            else:
                writer.writerow(row)
    shutil.move(mirokHome + "\\outputfile.txt", mirokHome + "\\default_files.txt")


# convert a ndarray to a gdx raster
def gdx_raster_from_array(input_array, array_type="float32", cell_size=100):
    meta = gdx.raster_metadata(rows=input_array.shape[0], cols=input_array.shape[1])
    meta.xll = 22000
    meta.yll = 153000
    meta.cell_size = cell_size
    gdx_raster = gdx.raster_from_ndarray(input_array.astype(array_type), meta)
    return gdx_raster


# rasterize a specific feature of a shape with gdx and return as array
def gdx_rasterized_shape_from_feature_as_array(input_file, category, category_value, output_shape_tuple):
    datasource = ogr.Open(input_file)
    layer = datasource.GetLayer(0)
    # select feature from shape and save it as shp file
    source_layer = datasource.ExecuteSQL(
        "SELECT * FROM %s WHERE %s = '%s'" % (str(layer.GetName()), category, category_value))
    drv = ogr.GetDriverByName('ESRI Shapefile')
    outds = drv.CreateDataSource(mirokHome + "\\temp.shp")
    outlyr = outds.CopyLayer(source_layer, 'temp')
    del outlyr, outds, source_layer, layer, datasource, drv
    # rasterize and return as array
    result = rasterize_gdx_return_array(mirokHome + "\\temp.shp", output_shape_tuple)
    os.remove(mirokHome + "\\temp.shp")
    return result


# sort layers in qgis alphabetically
def sort_layers():
    root = QgsProject.instance().layerTreeRoot()
    layer_names_enum_dict = lambda listCh: {listCh[q[0]].layerName() + str(q[0]): q[1]
                                            for q in enumerate(listCh)}
    mLNED = layer_names_enum_dict(root.children())
    mLNEDkeys = mLNED.keys()
    mLNEDkeys.sort()
    mLNEDsorted = [mLNED[k].clone() for k in mLNEDkeys]
    root.insertChildNodes(0, mLNEDsorted)
    for n in mLNED.values():
        root.removeChildNode(n)
    # collapse all
    for c in root.children():
        c.setExpanded(False)


def process_calculations_and_update_excel(end_result, selection_file, project_location, sheet_name, legend=None, cell_size=100):
    if cell_size == 100:
        result_vlaanderen = load_mask_from_array(mirokHome + "\\vlaanderen.tif", end_result)
    else:
        result_vlaanderen = load_mask_from_array(mirokHome + "\\vlaanderen_10m.tif", end_result)
        result_vlaanderen = result_vlaanderen.astype(np.float16)
    # process selection if there is one
    if selection_file is not None:
        # process selection shapefile
        selection_result, selection = process_selection(result_vlaanderen, selection_file, project_location, cell_size=cell_size)
    else:
        selection_result = result_vlaanderen
        selection = None
    calculate_and_save_indicators(selection_result, result_vlaanderen, sheet_name, selection, selection_file, legend, cell_size=cell_size)


def gdx_cluster_id_with_obstacles_for_arrays(array, obstacle_array):
    return gdx.cluster_id_with_obstacles(gdx_raster_from_array(array), gdx_raster_from_array(obstacle_array, "uint8"))


def gdx_sum_in_buffer_for_array(in_array, buffer_size, array_type="float32", cell_size=100):
    return gdx.sum_in_buffer(gdx_raster_from_array(in_array, array_type, cell_size), buffer_size).ndarray


def gdx_travel_distance_for_array(input_array, obstacle_array):
    return gdx.travel_distance(gdx_raster_from_array(input_array, "uint8"), obstacle_array).ndarray


def gdx_csum_with_arrays(input_array, second_array):
    return gdx.csum(gdx_raster_from_array(input_array, "int"),
                    gdx_raster_from_array(np.ones_like(second_array))).ndarray


def load_open_street_maps():
    if not QgsMapLayerRegistry.instance().mapLayersByName("OSM"):
        lyr = QgsRasterLayer(mirokHome + "\\vlaanderen.tif", "Vlaanderen")
        QgsMapLayerRegistry.instance().addMapLayer(lyr)
        canvas = iface.mapCanvas()
        canvas.zoomToFullExtent()
        QTimer.singleShot(10, load_osm)


def load_osm():
    QgsMapLayerRegistry.instance().removeAllMapLayers()
    lyr = QgsRasterLayer("type=xyz&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png", "OSM", "wms")
    QgsMapLayerRegistry.instance().addMapLayer(lyr)


def open_support_maps():
    load_layer(mirokHome + "\\gebiedstypering_volgens_bevolking123.tif", "Gebiedstypering Bevolking", mirokHome + "\\legende_gebiedstypering.qml")
    load_layer(mirokHome + "\\gebiedstypering_volgens_bebouwing123.tif", "Gebiedstypering Bebouwing", mirokHome + "\\legende_gebiedstypering.qml")
    load_layer(mirokHome + "\\gebiedstypering_volgens_basisvoorzieningen123.tif", "Gebiedstypering Voorzieningen", mirokHome + "\\legende_gebiedstypering.qml")
