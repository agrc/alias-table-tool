import os


class Input(object):
    
    #: path to roads feature class
    roads_feature = ""
    
    #: sgid county boundaries
    #: i've deleted all extra attributes besides the necessary ones and NAME
    county_features = ""
    
    #: sgid municipal boundaries
    #: i've deleted all extra attributes besides the necessary ones and NAME
    city_features = ""
    
    #: SGID LRS route feature class
    lrs_routes = ""
    
    def __init__(self, roads_featurePath, county_featuresPath, city_featuresPath, lrs_routesPath):
        self.roads_feature = roads_featurePath
        self.county_features = county_featuresPath
        self.city_features = city_featuresPath
        self.lrs_routes = lrs_routesPath

class Output(object):
    
    _arcpy = None
    #: folder to hold output geodata
    output = ""
    
    def __init__(self, arcpy, outputDirectory):
        self._arcpy = arcpy
        self.output = outputDirectory
        self.workspace = os.path.join(self.output, self.geodatabase)
        
    def startup(self):
        self._arcpy.CreateFileGDB_management(self.output, self.geodatabase)
        
    @property
    def csv_file(self):
        return os.path.join(self.output, self.csv)
            
    
    #: geodatabase workspace where output is stored
    workspace = ""
    
    #: output file geodatabase name
    geodatabase = "AliasTable.gdb"
    
    #: geodatabase feature class name
    table_name = "StreetAlias"
    
    #: name of the output csv results
    csv = "traverse.csv"
     
    #: fields to create in output for feature class and csv
    schema = {"alias_id": "STREET_ADDSYS",
              "low_milepost": "FROMMEASURE",
              "high_milepost": "TOMEASURE",
              "route_name": "RT_NAME",
              "field_used": "ALIASLEVEL"
              }
    
    #: temporary table for holding unique route names
    @property
    def _intermediate_frequency_output(self):
        name = "_frequency"
        return os.path.join(self.workspace, name)
        
    
    #: temp location for county identity
    @property
    def _intermediate_identity_county(self):
        name = "_identity_county"
        return os.path.join(self.workspace, name)
    
    #: temp location for city identity
    @property
    def _intermediate_identity_city_and_county(self):
        name = "_identity_city_and_county"
        return os.path.join(self.workspace, name)
    
    #: temp location for feature to vertices
    @property
    def _intermediate_feature_to_vertices(self):
        name = "_feature_to_vertice"
        return os.path.join(self.workspace, name)
 
    #: temp location for new milepost values   
    @property
    def _intermediate_mileposts_along_route(self):
        name = "_mileposts_along_route"
        return os.path.join(self.workspace, name)

    
    #: temp location for single part data
    @property
    def _intermediate_singlepart_data(self):
        name = "_singlepart_data"
        return os.path.join(self.workspace, name)

class Fields(object):
    
    #: prefix direction
    pre_dir = "PREDIR" #"PRE_DIR"
    
    #: suffix direction
    suffix_dir = "SUFDIR" #"SUF_DIR"
    
    #: street type
    street_type = "STREETTYPE" #"S_TYPE"
    
    #: street name
    street_name = "STREETNAME" #"S_NAME"
    
    #: first road name alias field
    alias = "ALIAS1"
    
    #: first road alias type
    alias_type = "ALIAS1TYPE" #"ALIAS1_TYP"
    
    #: second road name alias
    alias2 = "ALIAS2"

    #: second road name alias type
    alias2_type = "ALIAS2TYPE" #"ALIAS2_TYP"
    
    #: address coordindate system name
    acs_name = "ACSNAME" #"ACS_NAME"
    
    #: address coordinate system suffix
    acs_suffix =  "ACSSUF" #"ACS_SUF"
    
    #: address grid field
    address_grid = "ADDR_SYS" #"ADDRESS_SYS"
    
    #: from milepost
    from_milepost = "DOT_F_MILE" #"DOT_F_MP"
    
    #: to milepost
    to_milepost = "DOT_T_MILE" #"DOT_T_MP"
    
    #; route name
    route_name = "DOT_RTNAME"

    #: county name
    county_name = "NAME"
    
    #: city name
    city_name = "NAME_1"


class Alias(object):
    
    #: reference to field configuration
    _fields = None
        
    #: unique alias combinations
    alias_combination = None
    
    def __init__(self):
        self._fields = Fields()

        self.alias_combination = {
        "STREETKEY": [self._fields.pre_dir, self._fields.street_name, self._fields.suffix_dir,
                    self._fields.street_type, self._fields.county_name, self._fields.city_name,
                    self._fields.alias, self._fields.alias_type, self._fields.alias2, 
                    self._fields.alias2_type, self._fields.acs_name, self._fields.acs_suffix]
                    }