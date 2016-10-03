class RoadAlias(object):
    
    #: the route name
    route = None
    
    #: the milepost the road segment starts at
    from_milepost = None
    
    #: the milepost the road segment ends at
    to_milepost = None
    
    #: the combination of values of the data from the Alias.alias_combinations fields
    alias_key = None
    
    #: the alias name combination that was used to create the alias key
    alias_name = None
    
    aliasKeyFields = None
    
    def __init__(self, route, from_milepost, to_milepost, alias_key, alias_name):
        self.route = route
        self.from_milepost = from_milepost
        self.to_milepost = to_milepost
        self.alias_key = str(alias_key)
        self.aliasKeyFields = alias_key
        self.alias_name = alias_name
        
        
    @property
    def unique_key(self):
        return "{}{}{}".format(self.route, self.alias_key, self.alias_name)
    
    @property
    def csv(self):
        return [self.route, self.from_milepost, self.to_milepost, 
                self.aliasKeyFields.pre_dir, self.aliasKeyFields.street_name,
                self.aliasKeyFields.street_type, self.aliasKeyFields.suffix_dir,
                self.aliasKeyFields.alias, self.aliasKeyFields.alias_type,
                self.aliasKeyFields.alias2, self.aliasKeyFields.alias2_type,
                self.aliasKeyFields.acs_name, self.aliasKeyFields.acs_suffix,
                self.aliasKeyFields.county_name, self.aliasKeyFields.city_name]
    
    
class AliasKey(object):
    #Field contents for output CSV
    #: prefix direction
    pre_dir = ""
  
    #: street name
    street_name = ""
    #: street type
    street_type = ""
    
    #: suffix direction
    suffix_dir = ""
    
    #: first road name alias field
    alias = ""
    
    #: first road alias type
    alias_type = ""
    
    #: second road name alias
    alias2 = ""

    #: second road name alias type
    alias2_type = ""
    
    #: address coordindate system name
    acs_name = ""
    
    #: address coordinate system suffix
    acs_suffix = ""
    
    #: county name
    county_name = ""
    
    #: city name
    city_name = ""
    
    def __init__(self, pre_dir, suffix_dir, street_type, street_name, 
                 alias, alias_type, alias2, alias2_type, acs_name, 
                 acs_suffix, county_name, city_name):
       
        self.pre_dir = self._convertValueIfEmpty(pre_dir)
        self.street_name = self._convertValueIfEmpty(street_name)
        self.street_type = self._convertValueIfEmpty(street_type)
        self.suffix_dir = self._convertValueIfEmpty(suffix_dir)
        self.alias = self._convertValueIfEmpty(alias)
        self.alias_type = self._convertValueIfEmpty(alias_type)
        self.alias2 = self._convertValueIfEmpty(alias2)
        self.alias2_type = self._convertValueIfEmpty(alias2_type)
        self.acs_name = self._convertValueIfEmpty(acs_name)
        self.acs_suffix = self._convertValueIfEmpty(acs_suffix)
        self.county_name = self._convertValueIfEmpty(county_name)
        self.city_name = self._convertValueIfEmpty(city_name)
        
    def __str__(self):
        strParts = []
        if not self.pre_dir == "":
            strParts.append(self.pre_dir)
            
        if not self.street_name == "":
            strParts.append(self.street_name)

        if not self.street_type == "":
            strParts.append(self.street_type)
            
        if not self.suffix_dir == "":
            strParts.append(self.suffix_dir)
                     
        if not self.alias == "":
            strParts.append(self.alias)
            
        if not self.alias_type == "":
            strParts.append(self.alias_type)
            
        if not self.alias2 == "":
            strParts.append(self.alias2)
            
        if not self.alias2_type == "":
            strParts.append(self.alias2_type)
            
        if not self.acs_name == "":
            strParts.append(self.acs_name)
            
        if not self.acs_suffix == "":
            strParts.append(self.acs_suffix)
        
        if not self.county_name == "":
            strParts.append(self.county_name)

        if not self.city_name == "":
            strParts.append(self.city_name)
                    
        return " ".join(strParts)
    
    def _convertValueIfEmpty(self, value):
        if str(value).strip() == "" or value is None:
            return ""
        else:
            return str(value)
    