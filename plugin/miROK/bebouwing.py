import os
import mirok_tools as tools
import numspataggr
import numpy as np

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\gebiedstype2bebouwing"


def run(bebouwing_invoer, progress_bar, info, save_default):
    progress_bar.setValue(10)
    info.append("open input")
    bebouwing_invoer = tools.handle_input_file(bebouwing_invoer, save_default, 'B', "start", prj)

    gebouwen_10m = tools.rasterize_shape(bebouwing_invoer, "value", 10).ReadAsArray().astype("int8")

    progress_bar.setValue(30)
    info.append("clusterize buildings")
    a = tools.gdx_sum_in_buffer_for_array(gebouwen_10m, 50, array_type="uint8", cell_size=10)
    b = tools.gdx_sum_in_buffer_for_array(np.ones_like(gebouwen_10m), 50, array_type="uint8", cell_size=10)
    result = 100.0 * a / b
    del gebouwen_10m, a, b

    progress_bar.setValue(50)
    info.append("aggregate")
    out_data = numspataggr.rebin_avg(result, (result.shape[0] / 10, result.shape[1] / 10))
    del result

    progress_bar.setValue(80)
    info.append("recategorize")
    out_data = np.select([
        (out_data >= 0) & (out_data <= 7.4999),
        (out_data > 7.4999) & (out_data <= 14.999),
        (out_data > 14.999)],
        [1, 2, 3])

    out_data = tools.load_mask_from_array(mirokHome + "\\vlaanderen.tif", out_data)

    info.append("save result")
    tools.save_array_as_tif(mirokHome + "\\gebiedstypering_volgens_bebouwing123.tif", out_data)
    out_data_10m = numspataggr.rebin(out_data, (out_data.shape[0] * 10, out_data.shape[1] * 10), "sum")
    tools.save_array_as_tif(mirokHome + "\\gebiedstypering_volgens_bebouwing123_10m.tif", out_data_10m, cell_size=10)
    progress_bar.setValue(100)
