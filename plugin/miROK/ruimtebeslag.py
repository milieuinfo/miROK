import os
import mirok_tools as tools

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\2ruimtebeslag"


def run_indicator(input_file, selection, progress, info, save_default=False):
    progress.setValue(10)
    info.append("Converting 10m raster to 100m raster")
    input_file = tools.handle_input_file(input_file, save_default, '2', "start", prj)

    output_file = prj + "\\ruimtebeslag_100m.tif"

    info.append("open input file and convert to correct format")
    starting_array100m = tools.open_input_as_array(input_file)
    progress.setValue(30)

    info.append("save output 100m raster tif")
    progress.setValue(40)
    tools.save_array_as_tif_and_load_as_layer(output_file, "Ruimtebeslag", prj + "\\legend2.qml", starting_array100m)

    progress.setValue(70)

    tools.process_calculations_and_update_excel(starting_array100m, selection, prj, '2_ruimtebeslag', [0.25, 0.5, 0.75, 1])
    progress.setValue(100)
