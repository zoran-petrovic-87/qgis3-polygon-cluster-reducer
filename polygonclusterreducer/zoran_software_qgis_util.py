# -*- coding: utf-8 -*-
""""The zoran-software.com QGIS utility module."""
from typing import List
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsWkbTypes, QgsField, QgsVectorLayer, QgsFeature, QgsDistanceArea
from qgis.core import QgsSymbol, QgsRuleBasedRenderer


class ZoranSoftwareQgisUtil:
    """"The utility class."""

    @staticmethod
    def is_valid_polygon_selection(layer: QgsVectorLayer) -> bool:
        """"Checks if the layer type is polygon and if anything is selected."""
        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Unsupported layer type!")
            msg.setInformativeText("Please select polygon layer.")
            msg.setWindowTitle("Info")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return False
        if not layer.selectedFeatures():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Please select at least one feature!")
            msg.setWindowTitle("Info")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return False
        return True

    @staticmethod
    def create_field_int(layer: QgsVectorLayer, field_name: str) -> None:
        """Creates a new integer field if it does't exists."""
        field_index = layer.fields().indexFromName(field_name)
        if field_index == -1:
            layer.startEditing()
            newField = QgsField(field_name, QVariant.Int)
            layer.addAttribute(newField)
            layer.updateFields()

    @staticmethod
    def update_selected_features(
            layer: QgsVectorLayer,
            field_name: str,
            field_value) -> None:
        """Updates selected features to the specified value."""
        layer.startEditing()
        features = layer.selectedFeatures()
        for f in features:
            f[field_name] = field_value
            layer.updateFeature(f)
        layer.commitChanges()

    @staticmethod
    def update_feature(
            feature: QgsFeature,
            layer: QgsVectorLayer,
            field_name: str,
            field_value,
            commit: bool) -> None:
        """Updates feature to the specified value."""
        layer.startEditing()
        feature[field_name] = field_value
        layer.updateFeature(feature)
        if commit:
            layer.commitChanges()

    @staticmethod
    def set_rule_based_layer_style(
            layer: QgsVectorLayer,
            rules: List['StyleRule']) -> None:
        """Sets the rule based layer style."""
        # Create a new rule-based renderer.
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        renderer = QgsRuleBasedRenderer(symbol)
        # Get the "root" rule.
        root_rule = renderer.rootRule()
        for r in rules:
            # Create a clone (i.e. a copy) of the default rule.
            rule = root_rule.children()[0].clone()
            # Set the label, expression and color.
            rule.setLabel(r.label)
            rule.setFilterExpression(r.expression)
            rule.symbol().setColor(QColor(r.color_name))
            rule.symbol().setOpacity(r.opacity)
            # Set the scale limits if they have been specified.
            if r.scale_min_denom is not None and r.scale_max_denom is not None:
                rule.setScaleMinDenom(r.scale_min_denom)
                rule.setScaleMaxDenom(r.scale_max_denom)
            # Append the rule to the list of rules.
            root_rule.appendChild(rule)
        # Delete the default rule.
        root_rule.removeChildAt(0)
        # Apply the renderer to the layer.
        layer.setRenderer(renderer)

    @staticmethod
    def area(feature: QgsFeature) -> float:
        """Calculates an area of the feature."""
        return feature.geometry().area()

class StyleRule:
    """Class used for storing a rule for rule based layer style"""

    def __init__(
            self,
            label: str,
            expression: str,
            color_name: str,
            scale_min_denom: int,
            scale_max_denom: int,
            opacity: float):
        self.label = label
        self.expression = expression
        self.color_name = color_name
        self.scale_min_denom = scale_min_denom
        self.scale_max_denom = scale_max_denom
        # opacity value between 0 (fully transparent) and 1 (fully opaque).
        self.opacity = opacity
