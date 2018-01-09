import os

import mirok_tools as tools

import win32com.client as win32
import geluidsvervuiling, knooppuntwaarde, groenblauwenetwerken, groentypologieen, \
    luchtverontreiniging, nabijheidvanbasisvoorzieningen, openruimte, ruimtebeslag, hittekaart, gesaneerdegronden, overstroming, bebouwingstypologieen

from qgis.core import QgsProject

##miROK=group
##selectie= optional vector
##uitvoer_laag_100m=output file


mirokHome = os.environ['MIROK']


def run(selectie, total_progress_bar, progress_bar, progress_info):
    save_default = False
    group = QgsProject.instance().layerTreeRoot().insertGroup(0, "run")
    total_progress_bar.setValue(5)
    progress_info.append("Indicator 1 Bebouwingstypologieen")
    bebouwingstypologieen.run_indicator(None, selectie, progress_bar, progress_info, save_default)
    total_progress_bar.setValue(10)
    progress_info.append("Indicator 2 ruimtebeslag")
    ruimtebeslag.run_indicator(None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(20)
    progress_info.append("Indicator 3 Nabijheid van basisvoorzieningen")
    nabijheidvanbasisvoorzieningen.run_indicator(None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(30)
    progress_info.append("Indicator 4 open ruimte")
    openruimte.run_indicator(None, None, None, None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(40)
    progress_info.append("Indicator 5 Groenblauwenetwerken")
    groenblauwenetwerken.run_indicator(None, None, None, None, None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(50)
    progress_info.append("Indicator 6 Luchtverontreiniging")
    progress_info.append("Indicator 6.1 no2")
    luchtverontreiniging.run_indicator(None, selectie, progress_bar, progress_info, "no2", save_default)
    progress_info.append("Indicator 6.2 o3")
    luchtverontreiniging.run_indicator(None, selectie, progress_bar, progress_info, "o3", save_default)
    progress_info.append("Indicator 6.3 pm25")
    luchtverontreiniging.run_indicator(None, selectie, progress_bar, progress_info, "pm25", save_default)

    total_progress_bar.setValue(60)
    progress_info.append("Indicator 7 Hittekaart")
    hittekaart.run_indicator(None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(65)
    progress_info.append("Indicator 8 Percentage gesaneerde gronden")
    gesaneerdegronden.run_indicator(None, None, None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(70)
    progress_info.append("Indicator 9 groentypologieen")
    groentypologieen.run_indicator(None, None, None, None, None, None, None, None, selectie, progress_bar, progress_info, save_default)

    total_progress_bar.setValue(75)
    progress_info.append("Indicator 10 Overstromingshinderrisico")
    overstroming.run_indicator(selectie, progress_bar, progress_info)

    total_progress_bar.setValue(80)
    progress_info.append("Indicator 11 Geluidsvervuiling")
    progress_info.append("Indicator 11.1 weg")
    geluidsvervuiling.run_indicator(None, selectie, progress_bar, progress_info, "wegen", save_default)
    progress_info.append("Indicator 11.2 spoor")
    geluidsvervuiling.run_indicator(None, selectie, progress_bar, progress_info, "spoor", save_default)
    progress_info.append("Indicator 11.3 lucht")
    geluidsvervuiling.run_indicator(None, selectie, progress_bar, progress_info, "lucht", save_default)

    total_progress_bar.setValue(90)
    progress_info.append("Indicator 12 knooppuntwaarde")
    knooppuntwaarde.run_indicator(None, selectie, progress_bar, progress_info, save_default)

    # progress_info.append("sorting layers")
    # sort layers alphabetically
    # tools.sort_layers()

    tools.open_support_maps()

    progress_info.append("open Excel")
    # open excel file for user
    try:
        excel = win32.client.GetActiveObject("Excel.Application")
        print("Running Excel instance found, returning object")

    except:
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True
        print("No running Excel instances, returning new instance")

    wb = excel.Workbooks.Open(mirokHome + '\\gebiedstype_analyse_results.xlsx')
    if wb is not None:
        ws = wb.Sheets('samenvatting').Activate()
