import os
import mirok_tools as tools

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\11geluidsvervuiling"


def run_indicator(input_file, selection, progress_bar, info, sub_type, save_default):
    progress_bar.setValue(10)
    input_file = tools.handle_input_file(input_file, save_default, '11', sub_type, prj)

    output_file = prj + "\\geluidsvervuiling" + sub_type + ".tif"

    info.append("load input file and convert to correct format")
    starting_array100m = tools.open_input_as_array(input_file)

    info.append("save output 100m raster tif")
    tools.save_array_as_tif_and_load_as_layer(output_file, "Geluidsbelasting " + sub_type, prj + "\\Legend11.qml", starting_array100m)
    progress_bar.setValue(50)

    tools.process_calculations_and_update_excel(starting_array100m, selection, prj, '10_geluid_' + sub_type, [55, 60, 65, 70, 75])
    progress_bar.setValue(100)
