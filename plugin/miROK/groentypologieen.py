import os
import mirok_tools as tools
import numpy as np
import gdx

# ===============================================================================
# Environment Variable "MIROK" needs to point to the base folder of the miROK installation
# ===============================================================================

mirokHome = os.environ['MIROK']
prj = mirokHome + "\\9groentypologieen"


def run_indicator(input_file, wegen, spoor, water, park_file, beheer_file, grb_water_file, inwoners_file, selection, progress_bar, info, save_default):
    progress_bar.setValue(10)
    input_file = tools.handle_input_file(input_file, save_default, '9', "start", prj)
    wegen = tools.handle_input_file(wegen, save_default, '9', "wegen", prj)
    spoor = tools.handle_input_file(spoor, save_default, '9', "spoor", prj)
    water = tools.handle_input_file(water, save_default, '9', "water", prj)
    park_file = tools.handle_input_file(park_file, save_default, '9', "park", prj)
    beheer_file = tools.handle_input_file(beheer_file, save_default, '9', "beheer", prj)
    grb_water_file = tools.handle_input_file(grb_water_file, save_default, '9', "grb_water", prj)
    inwoners_file = tools.handle_input_file(inwoners_file, save_default, '9', "inwoners", prj)
    # //!Landgebruikskaart 100m
    info.append("load input and reclassify")
    starting_array100m = tools.open_input_as_array(input_file)
    progress_bar.setValue(20)
    starting_array100m_no_nan = np.where(np.isnan(starting_array100m), 0, starting_array100m)
    lu_natuurbos = np.select([
        (starting_array100m_no_nan >= 5) & (starting_array100m_no_nan <= 39),
        (starting_array100m_no_nan >= 79) & (starting_array100m_no_nan <= 91)], [1, 1], 0)

    niet_bebouwd = np.select([
        (starting_array100m_no_nan >= 1) & (starting_array100m_no_nan <= 84),
        (starting_array100m_no_nan >= 86) & (starting_array100m_no_nan <= 87),
        (starting_array100m_no_nan >= 90) & (starting_array100m_no_nan <= 91),
        (starting_array100m_no_nan >= 95) & (starting_array100m_no_nan <= 96),
        (starting_array100m_no_nan >= 99) & (starting_array100m_no_nan <= 100),
        (starting_array100m_no_nan >= 103) & (starting_array100m_no_nan <= 104),
        (starting_array100m_no_nan >= 109) & (starting_array100m_no_nan <= 110),
        (starting_array100m_no_nan >= 113) & (starting_array100m_no_nan <= 114),
        (starting_array100m_no_nan == 116)], [1, 1, 1, 1, 1, 1, 1, 1, 1], 0)
    progress_bar.setValue(30)
    # //parken lu-kaart VITO 10m, omgezet naar 100m, maar enkel behouden als geen bebouwde cellen op lu-kaartkaart NARA 100m.
    park = np.nan_to_num(tools.open_input_as_array(park_file))
    park = np.where(niet_bebouwd == 1, park, 0)
    beheerd = np.nan_to_num(tools.open_input_as_array(beheer_file))
    natuurbos = np.logical_or.reduce((beheerd, park, lu_natuurbos)).astype(int)
    landbouw = np.select([(starting_array100m_no_nan >= 41) & (starting_array100m_no_nan <= 78)], [1], 0)
    obstakels = calculate_obstacles(starting_array100m, spoor, water, wegen)
    progress_bar.setValue(40)
    grb_water = np.nan_to_num(tools.open_input_as_array(grb_water_file))
    water_opp = np.select([(starting_array100m_no_nan == 116)], [1], 0)
    klein_water = np.logical_and(water_opp, grb_water).astype(int)

    k = 30000
    progress_bar.setValue(50)
    # calculate different clusters
    info.append("calucate cluster size")
    groen_cluster_gt600ha_opp, groen_clusterid_gt600ha = calculate_first(klein_water, landbouw, natuurbos, obstakels, 500, 600)
    progress_bar.setValue(52)
    groen_cluster_gt200ha_opp, groen_clusterid_gt200ha, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 500, 200, 600, groen_cluster_gt600ha_opp,
                                                                                   groen_cluster_gt600ha_opp, k, 1)
    progress_bar.setValue(54)
    groen_cluster_gt60ha_opp, groen_clusterid_gt60ha, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 300, 60, 200, previous_total,
                                                                                 groen_cluster_gt200ha_opp, k, 2)
    progress_bar.setValue(56)
    groen_cluster_gt30ha_opp, groen_clusterid_gt30ha, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 200, 30, 60, previous_total, groen_cluster_gt60ha_opp,
                                                                                 k, 3)
    progress_bar.setValue(56)
    groen_cluster_gt10ha_opp, groen_clusterid_gt10ha, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 100, 10, 30, previous_total, groen_cluster_gt30ha_opp,
                                                                                 k, 4)
    progress_bar.setValue(60)
    groen_cluster_gt5ha_opp, groen_clusterid_gt5ha, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 0, 5, 10, previous_total, groen_cluster_gt10ha_opp, k,
                                                                               5, False)
    progress_bar.setValue(62)
    groen_cluster_gt1ha_opp, groen_clusterid_gt1ha, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 0, 1, 5, previous_total, groen_cluster_gt5ha_opp, k, 6,
                                                                               False)
    progress_bar.setValue(64)
    groen_cluster_gt5are_opp, groen_clusterid_gt5are, previous_total = calculate(klein_water, landbouw, natuurbos, obstakels, 0, 1, 5, previous_total, groen_cluster_gt1ha_opp, k,
                                                                                 7, False, True)
    progress_bar.setValue(70)
    # RESULTAAT    GROENCLUSTERS
    groen_totaal_id_ha = groen_clusterid_gt600ha + groen_clusterid_gt200ha + groen_clusterid_gt60ha \
                         + groen_clusterid_gt30ha + groen_clusterid_gt10ha + groen_clusterid_gt5ha \
                         + groen_clusterid_gt1ha + groen_clusterid_gt5are

    groen_totaal_opp_100m = groen_cluster_gt600ha_opp + groen_cluster_gt200ha_opp + groen_cluster_gt60ha_opp \
                            + groen_cluster_gt30ha_opp + groen_cluster_gt10ha_opp + groen_cluster_gt5ha_opp \
                            + groen_cluster_gt1ha_opp + groen_cluster_gt5are_opp

    # LANDBOUWCLUSTERS
    landbouw = np.logical_and(landbouw, groen_totaal_id_ha == 0)
    landbouw_id_ha = tools.gdx_cluster_id_with_obstacles_for_arrays(landbouw, obstakels)
    landbouw_opp_ha = gdx.csum(landbouw_id_ha,
                               tools.gdx_raster_from_array(np.ones_like(landbouw_id_ha.ndarray))).ndarray

    progress_bar.setValue(80)

    inwoners = tools.open_input_as_array(inwoners_file)
    opp_groen = groen_totaal_opp_100m
    groen_1ha = np.where(opp_groen > 1, 1, 0)
    groen_10ha = np.where(opp_groen > 10, 1, 0)
    groen_30ha = np.where(opp_groen > 30, 1, 0)
    groen_60ha = np.where(opp_groen > 60, 1, 0)
    groen_200ha = np.where(opp_groen > 200, 1, 0)
    info.append("calculate travel distances")
    dist_obstakel = tools.gdx_raster_from_array(np.where(np.logical_and(inwoners > 0, wegen > 0), 1, 9000))
    buurtgroen = np.where(tools.gdx_travel_distance_for_array(groen_1ha, dist_obstakel) < 4, 1, 0)
    wijkgroen = np.where(tools.gdx_travel_distance_for_array(groen_10ha, dist_obstakel) < 8, 1, 0)
    stadsdeelgroen = np.where(tools.gdx_travel_distance_for_array(groen_30ha, dist_obstakel) < 16, 1, 0)
    stadsgroen = np.where(tools.gdx_travel_distance_for_array(groen_60ha, dist_obstakel) < 32, 1, 0)
    stadsbos = np.where(tools.gdx_travel_distance_for_array(groen_200ha, dist_obstakel) < 50, 1, 0)
    tools.save_array_as_tif(prj + "\\buurtgroen.tif", buurtgroen)
    tools.save_array_as_tif(prj + "\\wijkgroen.tif", wijkgroen)
    tools.save_array_as_tif(prj + "\\stadsdeelgroen.tif", stadsdeelgroen)
    tools.save_array_as_tif(prj + "\\stadsgroen.tif", stadsgroen)
    tools.save_array_as_tif(prj + "\\stadsbos.tif", stadsbos)
    info.append("combine travel distance maps")
    total = buurtgroen + wijkgroen + stadsdeelgroen + stadsgroen + stadsbos

    tools.save_array_as_tif_and_load_as_layer(prj + "\\groen_cluster_distance.tif", "Groenaanbod (excl. landbouw)", prj + "\\legend9.qml", total)

    tools.process_calculations_and_update_excel(total, selection, prj, '9_groentypologie', [1, 2, 3, 4, 5])
    progress_bar.setValue(100)


def calculate_obstacles(starting_array100m, spoor, water, wegen):
    wegen_array = tools.rasterize_gdx_return_array(wegen, starting_array100m.shape)
    spoor_array = tools.rasterize_gdx_return_array(spoor, starting_array100m.shape)
    water_array = tools.rasterize_gdx_return_array(water, starting_array100m.shape)
    obstakels = np.logical_or.reduce((wegen_array, spoor_array, water_array)).astype(int)
    return obstakels


def calculate_first(klein_water, landbouw, natuurbos, obstakels, cluster_size, cluster_area):
    perc_groen = tools.gdx_sum_in_buffer_for_array(natuurbos, cluster_size) / tools.gdx_sum_in_buffer_for_array(np.ones_like(natuurbos), cluster_size)
    natuurbos = np.nan_to_num(natuurbos)
    groen = get_landbouw_and_klein_water(klein_water, landbouw, natuurbos, perc_groen)
    groen_clusterid = tools.gdx_cluster_id_with_obstacles_for_arrays(groen, obstakels).ndarray
    # assign(groen_clusteropp, cSum(groen_clusterid, 1))
    groen_clusteropp = tools.gdx_csum_with_arrays(groen_clusterid, groen)
    groen_cluster_gt600ha_opp = np.where(groen_clusteropp > cluster_area, groen_clusteropp, 0)
    groen_clusterid_gt600ha = tools.gdx_cluster_id_with_obstacles_for_arrays(
        np.where(groen_cluster_gt600ha_opp > 0, groen_cluster_gt600ha_opp, 0), obstakels).ndarray
    return groen_cluster_gt600ha_opp, groen_clusterid_gt600ha


def calculate(klein_water, landbouw, natuurbos, obstakels, cluster_size, cluster_area_from, cluster_area_till,
              previous_total, previous_area, k, factor, klein_water_landbouw=True, are=False):
    if klein_water_landbouw:
        perc_groen = tools.gdx_sum_in_buffer_for_array(natuurbos, cluster_size) / tools.gdx_sum_in_buffer_for_array(np.ones_like(natuurbos), cluster_size)
        groen = np.where(previous_total == 0, 1, 0) * get_landbouw_and_klein_water(klein_water, landbouw, natuurbos, perc_groen)
    else:
        groen = np.multiply(np.nan_to_num(natuurbos), np.where(previous_total == 0, 1, 0))
    if are:
        groen = np.where(obstakels != 0, 0, groen)
    groen_clusterid = tools.gdx_cluster_id_with_obstacles_for_arrays(groen, obstakels).ndarray
    # assign(groen_clusteropp, cSum(groen_clusterid, 1))
    groen_clusteropp = tools.gdx_csum_with_arrays(groen_clusterid, groen)
    groen_cluster_opp = np.where(np.logical_and(np.greater(groen_clusteropp, cluster_area_from), np.less_equal(previous_area, cluster_area_till)), groen_clusteropp, 0)
    previous_total = np.logical_or(previous_total, groen_cluster_opp)
    groen_cluster_id_opp = (factor * k) + tools.gdx_cluster_id_with_obstacles_for_arrays(np.where(groen_cluster_opp > 0, groen_cluster_opp, 0), obstakels).ndarray
    groen_cluster_id_opp = np.where(groen_cluster_id_opp == (factor * k), 0, groen_cluster_id_opp)
    return groen_cluster_opp, groen_cluster_id_opp, previous_total


def get_landbouw_and_klein_water(klein_water, landbouw, natuurbos, perc_groen):
    return np.logical_or.reduce((np.nan_to_num(natuurbos), np.logical_and(klein_water, perc_groen >= 0.5), np.logical_and(landbouw, perc_groen >= 0.3))).astype(int)
