# -*- coding: utf-8 -*-
"""
/***************************************************************************
 miROK
                                 A QGIS plugin
 miROK
                             -------------------
        begin                : 2017-07-05
        copyright            : (C) 2017 by miROK
        email                : miROK@VITO.be
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load miROK class from file miROK.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .miROK import miROK
    return miROK(iface)
