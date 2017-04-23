import logging
import numpy as np
import re


class LinearScaling(object):
    def __init__(self, intercept, slope):
        self.intercept = intercept
        self.slope = slope

    def scale(self, data):
        return data * self.slope + self.intercept


class PolynomialScaling(object):
    def __init__(self, coefficients):
        self.coefficients = coefficients

    def scale(self, data):
        scaled_data = np.zeros_like(data, dtype=np.double)
        for i, scale_factor in enumerate(self.coefficients):
            scaled_data += scale_factor * data ** i
        return scaled_data


def get_scaling(obj):
    scale_index = _get_scale_index(obj.properties)
    if scale_index is None:
        return None

    scale_type = obj.properties['NI_Scale[%d]_Scale_Type' % scale_index]
    if scale_type == 'Polynomial':
        coefficients = [
            obj.properties[
                'NI_Scale[%d]_Polynomial_Coefficients[%d]' % (scale_index, i)]
            for i in range(4)]
        return PolynomialScaling(coefficients)
    elif scale_type == 'Linear':
        return LinearScaling(
            obj.properties["NI_Scale[%d]_Linear_Y_Intercept" % scale_index],
            obj.properties["NI_Scale[%d]_Linear_Slope" % scale_index])
    else:
        log.warning("Unsupported scale type: %s", scale_type)
        return None


_scale_regex = re.compile(r"NI_Scale\[(\d+)\]_Scale_Type")


def _get_scale_index(properties):
    matches = (_scale_regex.match(key) for key in properties.keys())
    try:
        return max(int(m.group(1)) for m in matches if m is not None)
    except ValueError:
        return None