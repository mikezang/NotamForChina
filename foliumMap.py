import folium

# 地図生成
folium_map = folium.Map(location=[35.690921, 139.700258],zoom_start=15)

# サークルマーカープロット(外径色は赤，内径色は青)
folium.CircleMarker(location=[35.690921, 139.700258], radius=40, 
                    color='#ff0000', fill_color='#0000ff').add_to(folium_map)

# 地図表示
folium_map.save('images/foliumMap.html')