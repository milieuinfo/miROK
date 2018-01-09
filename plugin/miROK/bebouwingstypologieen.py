import os
import mirok_tools as tools

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\1bebouwingstypologieen"


def run_indicator(input_file, selection, progress_bar, info, save_default):
    progress_bar.setValue(10)
    info.append("open input")
    input_file = tools.handle_input_file(input_file, save_default, '1', "start", prj)

    output_file = prj + "\\bebouwingstypologieen" + ".tif"
    info.append("load input file and convert to correct format")
    starting_array10m = tools.open_input_as_array(input_file, cell_size = 10)
    info.append("load 10m raster tif")
    tools.load_layer(input_file, "Bebouwingstypologieen", prj + "\\legend.qml", force_crs=True)
    progress_bar.setValue(50)
    info.append("process")
    tools.process_calculations_and_update_excel(starting_array10m, selection, prj, '1_bebouwingstypo', [0, 2, 3], cell_size = 10)
    progress_bar.setValue(100)

