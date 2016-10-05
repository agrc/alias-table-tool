import arcpy, os, config, csv
from arcpy.da import UpdateCursor, SearchCursor
from models import RoadAlias, AliasKey
version_number = '1.3'


class Main(object):
    _output = None
    _input = None
    _fields = config.Fields()
    _alias = config.Alias()

    def __init__(self, roads_featurePath, county_featuresPath, city_featuresPath, lrs_routesPath, outputDirectory):
        print "Main constructor"

        arcpy.env.overwriteOutput = True
        self._input = config.Input(roads_featurePath, county_featuresPath, city_featuresPath, lrs_routesPath)
        self._output = config.Output(arcpy, outputDirectory)

        self.delete_if_exists([self._output.workspace])
        self._output.startup()
        arcpy.env.workspace = self._output.workspace


    def delete_if_exists(self, datasets):
        print "deleting existing file geodatabase"


        for ds in datasets:
            if arcpy.Exists(ds):
                # arcpy.AddMessage("deleting temp data")
                arcpy.Delete_management(ds)


    def start(self):
        arcpy.AddMessage("version: {}".format(version_number))

        self.split_roads_by_boundaries()
        routes = self.recalculate_mileposts()
        aliases = self.create_aliases(routes)
        aliases = self.reduce_to_common_aliases(aliases)
        self.export_to_csv(aliases)
        self.delete_if_exists([self._output.workspace])

        arcpy.AddMessage("finished")
        return self._output.csv_file

    def split_roads_by_boundaries(self):
        arcpy.AddMessage("splitting the roads by county and city")
        #: Get county name on roads and split on county polygons
        arcpy.Identity_analysis(self._input.roads_feature,
                                self._input.county_features,
                                self._output._intermediate_identity_county)

        #: Use output from first identity to get city name and split on city polygons
        arcpy.Identity_analysis(self._output._intermediate_identity_county,
                                self._input.city_features,
                                self._output._intermediate_identity_city_and_county)

    def recalculate_mileposts(self):
        arcpy.AddMessage("recalculating mileposts")

        routes = self._get_unique_routes()

        #: Identity_analysis creates multipart features. Bust them up.
        arcpy.MultipartToSinglepart_management(self._output._intermediate_identity_city_and_county,
                                               self._output._intermediate_singlepart_data)

        #: Intermediate step to recalculate milepost values. Need to from values of road as points
        arcpy.FeatureVerticesToPoints_management(self._output._intermediate_singlepart_data,
                                                 self._output._intermediate_feature_to_vertices,
                                                "BOTH_ENDS")
        routesCompleted = 0
        totalRoutes = len(routes)
        for route in routes:
            #Limit Locatefeature with a def query
            #: Creates table with new milepost values
            if routesCompleted % 10 == 0:
                arcpy.AddMessage("route recalculations remaining: {}".format(totalRoutes - routesCompleted))
            route_with_direction = route
            route = route[:4]

            arcpy.MakeFeatureLayer_management(self._input.lrs_routes,
                                               "definitionQueryRoute{}".format(route),
                                               """{} = '{}'""".format(arcpy.AddFieldDelimiters(self._input.lrs_routes,
                                                                                               'RT_NAME'),
                                                                             route))

            self.delete_if_exists([self._output._intermediate_mileposts_along_route])

            arcpy.LocateFeaturesAlongRoutes_lr(in_features=self._output._intermediate_feature_to_vertices,
                                               in_routes="definitionQueryRoute{}".format(route),
                                               route_id_field="RT_NAME",
                                               radius_or_tolerance="50 Meter",
                                               out_table= self._output._intermediate_mileposts_along_route,
                                               out_event_properties="RID POINT MEAS",
                                               route_locations="FIRST",
                                               distance_field=False,
                                               zero_length_events="ZERO",
                                               in_fields="FIELDS",
                                               m_direction_offsetting=True)

            new_mileposts = self._get_new_milepost_values(route_with_direction)

            where_clause = """{} = '{}'""".format(arcpy.AddFieldDelimiters(self._output._intermediate_singlepart_data,
                                                                             self._fields.route_name),
                                                    route_with_direction)
            with UpdateCursor(self._output._intermediate_singlepart_data,
                             ("OID@", self._fields.from_milepost, self._fields.to_milepost),
                             where_clause) as cursor:
                for row in cursor:
                    original_feature_id = row[0]

                    if original_feature_id not in new_mileposts:
                        print "objectid: {} was not found along LRS Routes. Data mismatch?".format(original_feature_id)
                        continue

                    mileposts = sorted(new_mileposts[original_feature_id])

                    if len(mileposts) is not 2:
                        raise Exception("Road segment with id {} does not fall within a 50 meter diameter of LRS data. Fix data or update radius_or_tolerance value.".format(row[0]))

                    if mileposts[0] > mileposts[1]:
                        print "objectid: {} has to milepost smaller than from milepost. Data issue?".format(original_feature_id)

                    row[1] = mileposts[0]
                    row[2] = mileposts[1]

                    cursor.updateRow(row)
            routesCompleted += 1
        return routes

    def create_aliases(self, routes):
        arcpy.AddMessage("creating road aliases")

        route_aliases = []

        for route in routes:
            # arcpy.AddMessage("acting on {}".format(route))
            where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(self._output._intermediate_singlepart_data,
                                                                       self._fields.route_name),
                                             route)
            with SearchCursor(in_table=self._output._intermediate_singlepart_data,
                              field_names=(self._fields.to_milepost,
                                           self._fields.from_milepost,
                                           self._fields.pre_dir,
                                           self._fields.suffix_dir,
                                           self._fields.street_name,
                                           self._fields.street_type,
                                           self._fields.address_grid,
                                           self._fields.alias,
                                           self._fields.alias_type,
                                           self._fields.alias2,
                                           self._fields.alias2_type,
                                           self._fields.acs_name,
                                           self._fields.acs_suffix,
                                           self._fields.county_name,
                                           self._fields.city_name),
                              where_clause = where_clause,
                              sql_clause = (None, "ORDER BY {}".format(self._fields.from_milepost))) as cursor:
                for row in cursor:
                    to_milepost = self._set_milepost_value(row[0])
                    from_milepost = self._set_milepost_value(row[1])

                    for alias in self._alias.alias_combination.keys():
                        alias_key = AliasKey(row[self._get_index_from_key(self._fields.pre_dir)],
                                            row[self._get_index_from_key(self._fields.suffix_dir)],
                                            row[self._get_index_from_key(self._fields.street_type)],
                                            row[self._get_index_from_key(self._fields.street_name)],
                                            row[self._get_index_from_key(self._fields.alias)],
                                            row[self._get_index_from_key(self._fields.alias_type)],
                                            row[self._get_index_from_key(self._fields.alias2)],
                                            row[self._get_index_from_key(self._fields.alias2_type)],
                                            row[self._get_index_from_key(self._fields.acs_name)],
                                            row[self._get_index_from_key(self._fields.acs_suffix)],
                                            row[self._get_index_from_key(self._fields.county_name)],
                                            row[self._get_index_from_key(self._fields.city_name)])

                        route_aliases.append(RoadAlias(route, from_milepost, to_milepost, alias_key, alias))

        return route_aliases

    def reduce_to_common_aliases(self, aliases):
        arcpy.AddMessage("reducing the road aliases")

        reduced_aliases = []

        aliases.sort(key=lambda x: (x.route, x.alias_name, x.from_milepost))

        i = 1
        size = len(aliases)
        current_unique_alias = aliases[0]

        while i < size:
            to_milepost = set([current_unique_alias.to_milepost])
            from_milepost = set([current_unique_alias.from_milepost])

            alias = aliases[i]

            while current_unique_alias.unique_key == alias.unique_key:
                to_milepost.add(alias.to_milepost)
                from_milepost.add(alias.from_milepost)

                i += 1
                if i >= size:
                    break

                alias = aliases[i]

            current_unique_alias.from_milepost = min(from_milepost)
            current_unique_alias.to_milepost = max(to_milepost)

            reduced_aliases.append(current_unique_alias)

            if i >= size:
                break

            current_unique_alias = aliases[i]
            i += 1

        return reduced_aliases

    def export_to_csv(self, aliases):
        arcpy.AddMessage("exporting to csv")

        with open(self._output.csv_file, 'wb') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(["RT_NAME", "FromMeasure", "ToMeasure",
                             self._fields.pre_dir, self._fields.street_name,  self._fields.street_type,
                             self._fields.suffix_dir, self._fields.alias, self._fields.alias_type,
                             self._fields.alias2, self._fields.alias2_type, self._fields.acs_name,
                             self._fields.acs_suffix, "County", "City"])


            for row in aliases:
                writer.writerow(row.csv)

#            os.startfile(self._output.csv_file)

    def _get_index_from_key(self, name):

        if name == self._fields.pre_dir:
            return 2
        elif name == self._fields.street_name:
            return 4
        elif name == self._fields.alias:
            return 7
        elif name == self._fields.alias2:
            return 9
        elif name == self._fields.acs_name:
            return 11
        elif name == self._fields.suffix_dir:
            return 3
        elif name == self._fields.alias_type:
            return 8
        elif name == self._fields.alias2_type:
            return 10
        elif name == self._fields.acs_suffix:
            return 12
        elif name == self._fields.street_type:
            return 5
        elif name == self._fields.address_grid:
            return 6
        elif name == self._fields.county_name:
            return 13
        elif name == self._fields.city_name:
            return 14

    def _set_milepost_value(self, milepost):
        #: Defaults empty milepost value to 0
        milepost_str = str(milepost).strip()

        if milepost_str == "" or milepost is None:
            return 0

        return milepost

    def _get_unique_routes(self):
        print ":: getting unique route names"

        routes = set()

        arcpy.Frequency_analysis(self._input.roads_feature,
                                 self._output._intermediate_frequency_output,
                                 self._fields.route_name)

        with SearchCursor(self._output._intermediate_frequency_output, self._fields.route_name) as cursor:
            for row in cursor:
                routes.add(row[0])

        return routes

    def _get_new_milepost_values(self, route):
        #: Iterates temp milepost values and appends to and from values for each original feature id
        #: Since each line was converted to a start and end point, every line should have two entries

        new_mileposts = {}

        where_clause = """"{}" = '{}'""".format(arcpy.AddFieldDelimiters(self._output._intermediate_mileposts_along_route,
                                                                         self._fields.route_name),
                                                route)
        with SearchCursor(self._output._intermediate_mileposts_along_route,
                          ("ORIG_FID", "MEAS"), where_clause) as cursor:
            for row in cursor:
                original_feature_id = row[0]
                milepost = row[1]

                if original_feature_id in new_mileposts:
                    new_mileposts[original_feature_id].append(milepost)
                    continue

                new_mileposts[original_feature_id] = [milepost]

        return new_mileposts
