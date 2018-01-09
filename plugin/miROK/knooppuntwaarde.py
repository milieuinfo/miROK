import os
import mirok_tools as tools

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================


mirokHome = os.environ['MIROK']
prj = mirokHome + "\\12knooppuntwaarde"


def run_indicator(input_file, selection, progress_bar, info, save_default):
    progress_bar.setValue(10)
    input_file = tools.handle_input_file(input_file, save_default, '12', "start", prj)

    starting_array100m = tools.open_input_as_array(input_file)
    progress_bar.setValue(30)

    output_file = prj + "\\knooppuntwaarde_100m.tif"
    progress_bar.setValue(40)

    info.append("save output 100m raster and load as layer")
    tools.save_array_as_tif_and_load_as_layer(output_file, "Knooppuntwaarde", prj + "\\legend12.qml", starting_array100m)

    progress_bar.setValue(60)

    tools.process_calculations_and_update_excel(starting_array100m, selection, prj, '12_knooppuntwaarde', [0, 1.126, 2.498, 4.293])
    progress_bar.setValue(100)
