"""Utility functions"""
__all__ = [
    "get_resource_path",
    "_return_t"
]

__author__ = ["Eshin Jolly"]
__license__ = "MIT"

import os
from rpy2.robjects.packages import importr

base = importr("base")


def get_resource_path():
    """Get path sample data directory."""
    return os.path.join(os.path.dirname(__file__), "resources") + os.path.sep


#def _return_t(model):
#    """Return t or z stat from R model summary."""
#    summary = base.summary(model)
#    unsum = base.unclass(summary)
#    return unsum.rx2("coefficients")[:, -1]





