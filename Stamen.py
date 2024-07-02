# -*- coding: utf-8 -*-
"""
地図タイル取得
--------------------

Stamenタイルサーバーからオンデマンドでダウンロードされる地図タイルを描画するcartopyの機能を示します。 
内部的にこれらのタイルは単一の画像に結合され、地図作成GeoAxesに表示されます。

"""
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


def main():
    # Stamen Terrainインスタンスを作成します。
    stamen_terrain = cimgt.StamenTerrain()

    # タイルの投影図にGeoAxesを作成します。
    ax = plt.axes(projection=stamen_terrain.crs)

    # 地図の範囲を小さい経度/緯度の範囲に制限します。
    ax.set_extent([-22, -15, 63, 65])

    # Stamenデータをズームレベル8で追加します。
    ax.add_image(stamen_terrain, 8)

    # Eyjafjallajökull火山のマーカーを追加します。
    plt.plot(-19.613333, 63.62, marker='o', color='red', markersize=12,
             alpha=0.7, transform=ccrs.Geodetic())

    # cartopyインターフェイスを使用して、測地座標系用のmatplotlib変換オブジェクトを作成します。 
    #これをmatplotlibのoffset_copy関数と一緒に使用して、テキストを左に25ピクセル移動する座標系を定義します。
    geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
    text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

    # 火山の左側に25ピクセルのテキストを追加します。
    plt.text(-19.613333, 63.62, u'Eyjafjallajökull',
             verticalalignment='center', horizontalalignment='right',
             transform=text_transform,
             bbox=dict(facecolor='sandybrown', alpha=0.5, boxstyle='round'))
    plt.show()


if __name__ == '__main__':
    main()