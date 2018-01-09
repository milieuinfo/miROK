import os
import mirok_tools as tools

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\6luchtverontreiniging"


def run_indicator(input_file, selection, progress_bar, info, sub_type, save_default):
    progress_bar.setValue(10)
    input_file = tools.handle_input_file(input_file, save_default, '6', sub_type, prj)

    output_file = prj + "\\luchtverontreiniging_" + sub_type + ".tif"

    info.append("open input file and convert to correct format")
    starting_array100m = tools.open_input_as_array(input_file)
    progress_bar.setValue(30)

    info.append("save output 100m raster tif")
    tools.save_array_as_tif_and_load_as_layer(output_file, "Luchtvervuiling " + sub_type, prj + "\\legend" + sub_type + ".qml", starting_array100m)

    progress_bar.setValue(50)

    legend = []
    print(sub_type)
    if sub_type == "no2":
        legend = [10, 15, 20, 25, 30, 35, 40, 45, 50]
    elif sub_type == "o3":
        legend = [0, 3.5, 7.5, 10.5, 15.5, 20.5, 25.5, 30.5, 40.5]
    elif sub_type == "pm25":
        legend = [5.5, 7.5, 10.5, 12.5, 15.5, 20.5, 25.5, 30.5, 35.5]
    tools.process_calculations_and_update_excel(starting_array100m, selection, prj, '6_' + sub_type, legend)
    progress_bar.setValue(100)
