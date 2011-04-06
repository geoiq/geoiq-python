# Wrapper around geoiq features + mapping to apis
#  Targets:
#    Raw,
#    Shapely,
#    Arc
import features
Feature = features.Feature

try:
    import shapely_features
except ImportError:
    pass
    
# TODO: 
# import arc_features
