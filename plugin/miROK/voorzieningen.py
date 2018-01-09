import os
import numpy as np
import mirok_tools as tools
import numspataggr


def run(voorzieningen_invoer, progress_bar, info, save_default):
    mirokHome = os.environ['MIROK']
    prj = mirokHome + "\\gebiedstype3basisvoorzieningen"

    progress_bar.setValue(10)
    info.append("open input")
    voorzieningen_invoer = tools.handle_input_file(voorzieningen_invoer, save_default, 'C', "start", prj)

    starting_array = tools.open_input_as_array(voorzieningen_invoer)

    progress_bar.setValue(50)
    info.append("recategorize raster")
    # recategorize raster
    out_data = np.select([
        (starting_array >= 0) & (starting_array <= 0.454),
        (starting_array > 0.454) & (starting_array <= 0.616),
        (starting_array > 0.616) & (starting_array < 1)],
        [1, 2, 3])

    out_data = tools.load_mask_from_array(mirokHome + "\\vlaanderen.tif", out_data)

    info.append("save result")
    tools.save_array_as_tif(mirokHome + "\\gebiedstypering_volgens_voorzieningen123.tif", out_data)
    out_data_10m = numspataggr.rebin(out_data, (out_data.shape[0] * 10, out_data.shape[1] * 10), "sum")
    tools.save_array_as_tif(mirokHome + "\\gebiedstypering_volgens_voorzieningen123_10m.tif", out_data_10m, cell_size=10)
    progress_bar.setValue(100)
