from lrs import Main
import arcpy
testing = False

if not testing:
    #: path to roads feature class
    roads_feature = arcpy.GetParameterAsText(0)
    # r"C:\KW_Working\Udot\AliasTable\ToolTesting\TestingInputLayers.gdb\Rt006"

    #: sgid county boundaries
    #: i've deleted all extra attributes besides the necessary ones and NAME
    county_features = arcpy.GetParameterAsText(1)
    # r"C:\KW_Working\Udot\AliasTable\ToolTesting\TestingInputLayers.gdb\counties"

    #: sgid municipal boundaries
    #: i've deleted all extra attributes besides the necessary ones and NAME
    city_features = arcpy.GetParameterAsText(2)
    # r"Database Connections\agrc@SGID10@gdb10.agrc.utah.gov.sde\SGID10.BOUNDARIES.Municipalities"

    #: SGID LRS route feature class
    lrs_routes = arcpy.GetParameterAsText(3)
    # r"Database Connections\agrc@SGID10@gdb10.agrc.utah.gov.sde\SGID10.TRANSPORTATION.UDOTRoutes_LRS"

    output = arcpy.GetParameterAsText(4)
    # r"C:\KW_Working\Udot\AliasTable\ToolTesting\Outputs"

else:
    roads_feature = r"C:\KW_Working\Udot\AliasTable\ToolTesting\MultiRtTest\TestLayers.gdb\rt_6_68"

    #: sgid county boundaries
    county_features = r"C:\KW_Working\Udot\AliasTable\ToolTesting\TestingInputLayers.gdb\counties"

    #: sgid municipal boundaries
    city_features = r"Database Connections\agrc@SGID10@gdb10.agrc.utah.gov.sde\SGID10.BOUNDARIES.Municipalities"

    #: SGID LRS route feature class
    lrs_routes = r"Database Connections\agrc@SGID10@gdb10.agrc.utah.gov.sde\SGID10.TRANSPORTATION.UDOTRoutes_LRS"

    output = r"C:\KW_Working\Udot\AliasTable\ToolTesting\debug\run4"


if __name__ == "__main__":
    this = Main(roads_feature, county_features, city_features, lrs_routes, output)
    outputLocation = this.start()
    if not testing:
        arcpy.SetParameterAsText(5, outputLocation)
