import os
import numpy as np
import mirok_tools as tools
import numspataggr

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\8percentagegesaneerdegronden"


def run_indicator(gesaneerd_file, ongesaneerd_file, project_file, selection, progress, info, save_default):
    progress.setValue(10)
    gesaneerd_file = tools.handle_input_file(gesaneerd_file, save_default, '8', "gesaneerd", prj)
    project_file = tools.handle_input_file(project_file, save_default, '8', "project", prj)
    ongesaneerd_file = tools.handle_input_file(ongesaneerd_file, save_default, '8', "ongesaneerd", prj)
    info.append("rasterize input files")
    gesaneerd = tools.rasterize_shape(gesaneerd_file, "value", 10, 0)
    gesaneerd = gesaneerd.ReadAsArray()
    progress.setValue(20)
    project = tools.rasterize_shape(project_file, "value", 10, 0)
    project = project.ReadAsArray()
    progress.setValue(30)
    ongesaneerd = tools.rasterize_shape(ongesaneerd_file, "value", 10, 0)
    ongesaneerd = ongesaneerd.ReadAsArray()
    progress.setValue(40)
    info.append("combine and rebin to 100m")
    gesaneerd_100 = numspataggr.rebin(gesaneerd, (gesaneerd.shape[0] / 10, gesaneerd.shape[1] / 10), "sum")
    # project - gesaneerd
    project = np.where(gesaneerd == 1, 0, project)
    # ongesaneerd - project - gesaneerd
    ongesaneerd = np.where(project == 1, 0, np.where(gesaneerd == 1, 0, ongesaneerd))
    progress.setValue(50)
    gesaneerd = None
    ongesaneerd_100 = numspataggr.rebin(ongesaneerd, (ongesaneerd.shape[0] / 10, ongesaneerd.shape[1] / 10), "sum")
    ongesaneerd = None
    project_100 = numspataggr.rebin(project, (project.shape[0] / 10, project.shape[1] / 10), "sum")
    project = None
    progress.setValue(60)
    # convert to signed int for negative values
    info.append("calculate final result")
    result = ((gesaneerd_100 + project_100 / 2) - ongesaneerd_100).astype("int")
    # set noData to -9999 to make it possible to have a color in the legend for it.
    result = np.where(result == 0, -9999, result)
    result = np.where(np.logical_and(result < 0, result >= -100), 0, result)
    output_file = prj + "\\percentage_gesaneerde_gronden_100m.tif"
    progress.setValue(70)

    info.append("save output 100m raster and load as layer")
    tools.save_array_as_tif_and_load_as_layer(output_file, "Percentage gesaneerde gronden", prj + "\\legend8.qml", result)
    progress.setValue(90)
    # set noData to NaN for calculations
    result = np.where(result == -9999, np.NaN, result)

    tools.process_calculations_and_update_excel(result, selection, prj, '8_bodemsanering', [-1, 5, 25, 50, 75, 95])
    progress.setValue(100)
