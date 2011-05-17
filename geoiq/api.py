
# Version-specific and URL-specific stuff!


class API(object):
    # Search-related urls & opts:
    search = "search.json"
    search_dataset_name = "Overlay"
    search_map_name = "Map"
    search_analysis_name = "Refinement"

    # dataset-related urls:
    dataset_by_id_url = "datasets/%(id)s.json?include_features=0"
    dataset_create_url = "datasets.json"
    dataset_update_feed_url = "datasets/%(id)s/fetch.json"
    dataset_features_url = "datasets/%(id)s/features.json?start=%(start)s&limit=%(limit)s&hex_geometry=1"
    dataset_download_url = "datasets/%(id)s.%(format)s"
    #dataset_analyze_url = "datasets/%(id)s/calculate.json"
    
    # Map-related urls:
    map_create_url = "maps.json"
    map_by_id_url = "maps/%(id)s.json"
    map_layer_add_url = "maps/%(id)s/layers.json"

    # User-related urls:
    user_create_url = "users.json"
    user_by_id_url = "users/%(id)s.json"

    # Group-related urls:
    group_create_url = "groups.json"
    group_by_id_url = "groups/$(id)s.json"

    # Analysis-related urls:
    analysis_go_url = "refiners" 
    analysis_by_id_url = "refinements/%(id)s.json"

class StagingAPI(API):
    # staging.geocommons.net changes:
    analysis_by_id_url = "refinement_types/%(id)s.json"
    analysis_go_url = "analysis.json" # TODO: should it always be there?
    search_analysis_name = "RefinementType"

