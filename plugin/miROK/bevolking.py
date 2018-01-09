import os
import numpy as np
import mirok_tools as tools
import numspataggr


def run(bevolking_invoer, progress_bar, info, save_default):
    mirokHome = os.environ['MIROK']
    prj = mirokHome + "\\gebiedstype1bevolking"

    progress_bar.setValue(10)
    info.append("open input")
    bevolking_invoer = tools.handle_input_file(bevolking_invoer, save_default, 'A', "start", prj)

    starting_array = tools.open_input_as_array(bevolking_invoer)

    progress_bar.setValue(50)
    info.append("recategorize raster")
    # recategorize raster
    out_data = np.select([
        (starting_array <= 6) | (starting_array >= 999),
        (starting_array > 6) & (starting_array < 40),
        (starting_array >= 40) & (starting_array < 999),
        np.isnan(starting_array)]
        ,
        [1, 2, 3, 1])
    print("t")
    info.append("save result")
    tools.save_array_as_tif(mirokHome + "\\gebiedstypering_volgens_bevolking123.tif", out_data)
    out_data_10m = numspataggr.rebin(out_data, (out_data.shape[0] * 10, out_data.shape[1] * 10), "sum")
    tools.save_array_as_tif(mirokHome + "\\gebiedstypering_volgens_bevolking123_10m.tif", out_data_10m, cell_size=10)
    progress_bar.setValue(100)
