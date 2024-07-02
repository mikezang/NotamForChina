import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geoplot
import geopandas as gpd

from myModules import myKml
from myModules import myShape

def plot2():
    # Load sample data
    kmlFile = '/users/w802479/downloads/2024年06月28日文昌长征七号甲.kml'
    gdf = myKml.readKmlFile(kmlFile)

    # Define the extent
    extent = myShape.getExtent(gdf)

    # Create a figure with a Cartopy projection
    # fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.Mercator()})

    # Set the extent
    # ax.set_extent(extent, crs=ccrs.PlateCarree())
    myShape.adjustLimitsExtent(ax, extent)

    # Plot each geometry in the GeoDataFrame
    for geom in gdf.geometry:
        if geom.geom_type == 'Polygon':
            lons, lats = geom.exterior.xy
            ax.plot(lons, lats, transform=ccrs.Geodetic(), color='blue', linewidth=0.5, zorder=2)
        elif geom.geom_type == 'MultiPolygon':
            lons, lats = geom.exterior.xy
            ax.plot(lons, lats, transform=ccrs.Geodetic(), color='blue', linewidth=0.5, zorder=2)
        elif geom.geom_type == 'LineString':
            lons, lats = geom.xy
            ax.plot(lons, lats, transform=ccrs.Geodetic(), color='blue', linewidth=0.5, zorder=2)
        elif geom.geom_type == 'MultiLineString':
            for line in geom:
                lons, lats = line.xy
                ax.plot(lons, lats, transform=ccrs.Geodetic(), color='blue', linewidth=0.5, zorder=2)

    # Add features (optional)
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='none')

    # Show the plot
    # plt.show()
    fig.savefig('temp/axPlotInsteadOfGeoplot.png', dpi=96)

# Create a figure
def plot1():
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.stock_img()
    ax.set_extent([90, 120, 45, 15])

    ny_lon, ny_lat = 100.3, 40.96666666666667
    delhi_lon, delhi_lat = 110.95, 19.616666666666667

    # geoplot.polyplot(gdf, ax=ax, extent=extent, facecolor='none', color=color, linewidth=0.5, zorder=zorder)

    plt.plot([ny_lon, delhi_lon], [ny_lat, delhi_lat],
            color='blue', linewidth=2, marker='o',
            transform=ccrs.Geodetic(),
            )

    plt.plot([ny_lon, delhi_lon], [ny_lat, delhi_lat],
            color='gray', linestyle='--',
            transform=ccrs.PlateCarree(),
            )

    plt.text(ny_lon - 3, ny_lat - 12, 'New York',
            horizontalalignment='right',
            transform=ccrs.Geodetic())

    plt.text(delhi_lon + 3, delhi_lat - 12, 'Delhi',
            horizontalalignment='left',
            transform=ccrs.Geodetic())

    # plt.show()
    fig.savefig('temp/googleMap.png', dpi=96)


if __name__ == "__main__":
    # plot1()
    plot2()