# -*- coding: utf-8 -*-
"""
/***************************************************************************
 miROK
                                 A QGIS plugin
 miROK
                              -------------------
        begin                : 2017-07-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by miROK
        email                : miROK@VITO.be
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import QgsVectorLayer, QgsRasterLayer
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from miROK_dialog import miROKDialog
import mirok_run as mirok
import geluidsvervuiling, knooppuntwaarde, groenblauwenetwerken, groentypologieen, \
    luchtverontreiniging, nabijheidvanbasisvoorzieningen, openruimte, ruimtebeslag, hittekaart, gesaneerdegronden, \
    bevolking, bebouwing, voorzieningen, overstroming, mirok_tools, bebouwingstypologieen
import os.path
import csv


class miROK:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'miROK_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&miROK')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('miROK', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = miROKDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/miROK/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'miROK'),
            callback=self.run,
            add_to_toolbar=True,
            parent=self.iface.mainWindow())
        self.dlg.startButton.clicked.connect(self.onStart)
        self.dlg.cancelButton.clicked.connect(self.onCancel)
        self.dlg.indicatorSelect.currentIndexChanged.connect(self.selectionChange)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        self.fill_comboboxes()
        self.init_interface()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.exec_()


    def init_interface(self):
        mirok_tools.load_open_street_maps()
        total_progress_bar = self.dlg.totalProgressBar
        total_progress_bar.setRange(0, 100)
        total_progress_bar.setValue(0)
        progress_bar = self.dlg.progressBar
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_info = self.dlg.logWindow
        progress_info.setText("")
        self.dlg.subSelect.setVisible(False)
        self.dlg.subLabel.setVisible(False)
        self.changeAllExtraFields(False)
        self.dlg.indicatorSelect.setCurrentIndex(-1)
        self.dlg.tabWidget.setCurrentIndex(0)
        self.dlg.startButton.setEnabled(True)
        self.dlg.cancelButton.setEnabled(True)

    def fill_comboboxes(self):
        self.add_open_vector_layers_to_combo_box()
        self.add_open_layers_to_combo_box(self.dlg.inputFileSelect)
        self.add_open_layers_to_combo_box(self.dlg.wegenSelect)
        self.add_open_layers_to_combo_box(self.dlg.spoorSelect)
        self.add_open_layers_to_combo_box(self.dlg.bevWaterSelect)
        self.add_open_layers_to_combo_box(self.dlg.waterlopenSelect)
        self.add_open_layers_to_combo_box(self.dlg.parkSelect)
        self.add_open_layers_to_combo_box(self.dlg.beheerSelect)
        self.add_open_layers_to_combo_box(self.dlg.inwonersSelect)

    def add_open_layers_to_combo_box(self, combo_box):
        layers = self.iface.legendInterface().layers()
        layer_list = ["Default"]
        for layer in layers:
            layer_list.append(layer.name() + " - " + layer.source())
        combo_box.clear()
        combo_box.addItems(layer_list)

    def add_open_vector_layers_to_combo_box(self):
        layers = self.iface.legendInterface().layers()
        layer_list = [""]
        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                layer_list.append(layer.name() + " - " + layer.source())
        self.dlg.shapeSelect.clear()
        self.dlg.shapeSelect.addItems(layer_list)
        self.dlg.indicatorShapeSelect.clear()
        self.dlg.indicatorShapeSelect.addItems(layer_list)

    def onStart(self):
        self.dlg.startButton.setEnabled(False)
        self.dlg.cancelButton.setEnabled(False)
        self.v = False  # verbose
        self.main()

    def onCancel(self):
        self.dlg.close()

    def main(self):
        progress_bar = self.dlg.progressBar
        total_progress_bar = self.dlg.totalProgressBar
        progress_info = self.dlg.logWindow
        layers = self.iface.legendInterface().layers()
        tab = self.dlg.tabWidget.currentIndex()
        if tab == 0:
            selection = self.getSelectedValue(self.dlg.shapeSelect)
            mirok.run(selection, total_progress_bar, progress_bar, progress_info)
        elif tab == 1:
            selection = self.getSelectedValue(self.dlg.indicatorShapeSelect)
            input_file = self.getSelectedValue(self.dlg.inputFileSelect)
            indicator = self.dlg.indicatorSelect.currentIndex()
            save_default = self.dlg.saveDefaultCheckBox.isChecked()

            if indicator == 0:
                bebouwingstypologieen.run_indicator(input_file, selection, progress_bar, progress_info, save_default)
            if indicator == 1:
                ruimtebeslag.run_indicator(input_file, selection, progress_bar, progress_info, save_default)
            if indicator == 2:
                nabijheidvanbasisvoorzieningen.run_indicator(input_file, selection, progress_bar, progress_info, save_default)
            if indicator == 3:
                wegen_input = self.getSelectedValue(self.dlg.wegenSelect)
                spoor_input = self.getSelectedValue(self.dlg.spoorSelect)
                water_input = self.getSelectedValue(self.dlg.bevWaterSelect)
                openruimte.run_indicator(input_file, wegen_input, spoor_input, water_input, selection, progress_bar, progress_info, save_default)
            if indicator == 4:
                wegen_input = self.getSelectedValue(self.dlg.wegenSelect)
                spoor_input = self.getSelectedValue(self.dlg.spoorSelect)
                water_input = self.getSelectedValue(self.dlg.bevWaterSelect)
                waterlopen_input = self.getSelectedValue(self.dlg.waterlopenSelect)
                groenblauwenetwerken.run_indicator(input_file, wegen_input, spoor_input, water_input, waterlopen_input, selection, progress_bar, progress_info, save_default)
            if indicator == 5:
                sub_type = self.dlg.subSelect.currentText()
                luchtverontreiniging.run_indicator(input_file, selection, progress_bar, progress_info, sub_type, save_default)
            if indicator == 6:
                hittekaart.run_indicator(input_file, selection, progress_bar, progress_info, save_default)
            if indicator == 7:
                # reuse input boxes
                gesaneerd_input = self.getSelectedValue(self.dlg.wegenSelect)
                ongesaneerd_input = self.getSelectedValue(self.dlg.spoorSelect)
                project_input = self.getSelectedValue(self.dlg.bevWaterSelect)
                gesaneerdegronden.run_indicator(gesaneerd_input, ongesaneerd_input, project_input, selection, progress_bar, progress_info, save_default)
            if indicator == 8:
                wegen_input = self.getSelectedValue(self.dlg.wegenSelect)
                spoor_input = self.getSelectedValue(self.dlg.spoorSelect)
                water_input = self.getSelectedValue(self.dlg.bevWaterSelect)
                park_input = self.getSelectedValue(self.dlg.parkSelect)
                beheer_input = self.getSelectedValue(self.dlg.beheerSelect)
                waterlopen_input = self.getSelectedValue(self.dlg.waterlopenSelect)
                inwoners_input = self.getSelectedValue(self.dlg.inwonersSelect)
                groentypologieen.run_indicator(input_file, wegen_input, spoor_input, water_input, park_input,
                                               beheer_input, waterlopen_input, inwoners_input, selection, progress_bar,
                                               progress_info, save_default)
            if indicator == 9:
                overstroming.run_indicator(selection,progress_bar, progress_info)
            if indicator == 10:
                sub_type = self.dlg.subSelect.currentText()
                geluidsvervuiling.run_indicator(input_file, selection, progress_bar, progress_info, sub_type, save_default)
            if indicator == 11:
                knooppuntwaarde.run_indicator(input_file, selection, progress_bar, progress_info, save_default)
            if indicator == 12:
                bevolking.run(input_file, progress_bar, progress_info, save_default)
            if indicator == 13:
                bebouwing.run(input_file, progress_bar, progress_info, save_default)
            if indicator == 14:
                voorzieningen.run(input_file, progress_bar, progress_info, save_default)

        self.onFinish(progress_bar, progress_info, total_progress_bar)

    def getSelectedValue(self, combo_box):
        value = str(combo_box.currentText())
        if value == "" or value == "Default":
            return None
        return value.split(" - ")[1]

    def onFinish(self, progress_bar, progress_info, total_progress_bar):
        total_progress_bar.setValue(0)
        progress_bar.setValue(0)
        progress_info.append("\n Done")
        self.dlg.startButton.setEnabled(True)
        self.dlg.cancelButton.setEnabled(True)

    def selectionChange(self):
        indicator = self.dlg.indicatorSelect.currentIndex()
        self.dlg.subSelect.setVisible(False)
        self.dlg.subLabel.setVisible(False)
        self.changeAllExtraFields(False)
        self.dlg.startButton.setEnabled(True)
        self.dlg.saveDefaultCheckBox.setChecked(False)
        self.resetLabels()
        if indicator == 3:
            self.enableWegenSpoorBevwaterFields()
        if indicator == 4:
            self.enableWegenSpoorBevwaterFields()
            self.dlg.waterlopenSelect.setVisible(True)
            self.dlg.waterlopenLabel.setVisible(True)
        if indicator == 5:
            self.enableSubSelect(6)
        if indicator == 7:
            self.dlg.wegenLabel.setText("Gesaneerd Input")
            self.dlg.spoorLabel.setText("Ongesaneerd Input")
            self.dlg.bevWaterLabel.setText("Saneringsproject Input")
            self.enableWegenSpoorBevwaterFields()
        if indicator == 8:
            self.changeAllExtraFields(True)
        if indicator == 10:
            self.enableSubSelect(11)


    def resetLabels(self):
        self.dlg.wegenLabel.setText("Wegen Input")
        self.dlg.spoorLabel.setText("Spoorwegen Input")
        self.dlg.waterlopenLabel.setText("Waterlopen Input")

    def changeAllExtraFields(self, boolean):
        self.dlg.wegenSelect.setVisible(boolean)
        self.dlg.wegenLabel.setVisible(boolean)
        self.dlg.spoorSelect.setVisible(boolean)
        self.dlg.spoorLabel.setVisible(boolean)
        self.dlg.bevWaterSelect.setVisible(boolean)
        self.dlg.bevWaterLabel.setVisible(boolean)
        self.dlg.waterlopenSelect.setVisible(boolean)
        self.dlg.waterlopenLabel.setVisible(boolean)
        self.dlg.parkSelect.setVisible(boolean)
        self.dlg.parkLabel.setVisible(boolean)
        self.dlg.beheerSelect.setVisible(boolean)
        self.dlg.beheerLabel.setVisible(boolean)
        self.dlg.inwonersSelect.setVisible(boolean)
        self.dlg.inwonersLabel.setVisible(boolean)

    def enableWegenSpoorBevwaterFields(self):
        self.dlg.wegenSelect.setVisible(True)
        self.dlg.wegenLabel.setVisible(True)
        self.dlg.spoorSelect.setVisible(True)
        self.dlg.spoorLabel.setVisible(True)
        self.dlg.bevWaterSelect.setVisible(True)
        self.dlg.bevWaterLabel.setVisible(True)

    def enableSubSelect(self, indicator):
        self.dlg.subSelect.setVisible(True)
        self.dlg.subLabel.setVisible(True)
        if indicator == 6:
            self.dlg.subSelect.clear()
            self.dlg.subSelect.addItem("no2")
            self.dlg.subSelect.addItem("o3")
            self.dlg.subSelect.addItem("pm25")
        if indicator == 11:
            self.dlg.subSelect.clear()
            self.dlg.subSelect.addItem("wegen")
            self.dlg.subSelect.addItem("spoor")
            self.dlg.subSelect.addItem("lucht")
