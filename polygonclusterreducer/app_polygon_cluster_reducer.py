# -*- coding: utf-8 -*-
""""The polygon cluster reducer module."""
from typing import List
from random import shuffle
from operator import itemgetter
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsWkbTypes, QgsField, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.utils import iface
from .zoran_software_qgis_util import ZoranSoftwareQgisUtil, StyleRule


class AppPolygonClusterReducer:
    """"The polygon cluster reducer class."""
    @staticmethod
    def run(
            field_name: str,
            search_radius: float,
            area_greater_than: float,
            area_less_than: float,
            is_random_order: bool,
            opacity_of_removed_features: float) -> List['QgsFeature']:
        """"Preforms cluster reduction."""
        canvas = iface.mapCanvas()
        layer = canvas.currentLayer()
        if not ZoranSoftwareQgisUtil.is_valid_polygon_selection(layer):
            return
        ZoranSoftwareQgisUtil.create_field_int(layer, field_name)
        ZoranSoftwareQgisUtil.update_selected_features(layer, field_name, 0)

        fs_rem = []
        fs = []

        for f in layer.selectedFeatures():
            a = ZoranSoftwareQgisUtil.area(f)
            fs.append({"feature": f, "area": a})

        if is_random_order:
            shuffle(fs)

        for i in range(0, len(fs)):
            fi = fs[i]["feature"]
            if fi[field_name] == 1:
                # Already removed.
                continue
            for j in range(i + 1, len(fs)):
                fj = fs[j]["feature"]
                if_less = fs[j]["area"] < area_less_than
                if_greater = fs[j]["area"] > area_greater_than
                if if_less and if_greater:
                    dist = fi.geometry().distance(fj.geometry())
                    if dist <= search_radius:
                        fs_rem.append(
                            {
                                "feature": fj,
                                "dist": dist,
                                "area": fs[j]["area"]
                            })

        new_list = sorted(fs_rem, key=itemgetter('dist'), reverse=True)

        for r in new_list:
            ZoranSoftwareQgisUtil.update_feature(
                r["feature"],
                layer,
                field_name,
                1,
                False)

        layer.commitChanges()

        rule1 = StyleRule(
            "Keep",
            '"' + field_name + '"=0 OR "' + field_name + '" IS null',
            'green',
            None,
            None,
            1.0)
        rule2 = StyleRule(
            "Remove",
            '"' + field_name + '" = 1',
            'red',
            None,
            None,
            opacity_of_removed_features)
        rules = []
        rules.append(rule1)
        rules.append(rule2)
        ZoranSoftwareQgisUtil.set_rule_based_layer_style(layer, rules)
        fs_sel = layer.selectedFeatures()
        layer.removeSelection()

        return fs_sel
