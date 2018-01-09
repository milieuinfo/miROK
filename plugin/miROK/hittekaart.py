import os
import mirok_tools as tools

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================


mirokHome = os.environ['MIROK']
prj = mirokHome + "\\7hittekaart"


def run_indicator(input_file, selection, progress, info, save_default):
    progress.setValue(10)
    input_file = tools.handle_input_file(input_file, save_default, '7', "start", prj)

    starting_array100m = tools.open_input_as_array(input_file)
    progress.setValue(30)

    output_file = prj + "\\hittekaart_100m.tif"
    progress.setValue(40)

    info.append("save output 100m raster and load as layer")
    tools.save_array_as_tif_and_load_as_layer(output_file, "Hittekaart", prj + "\\legend7.qml", starting_array100m)

    progress.setValue(60)

    tools.process_calculations_and_update_excel(starting_array100m, selection, prj, '7_hitte', [1])
    progress.setValue(100)
