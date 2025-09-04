# mapa.py
import geopandas as gpd
import folium

provincias = gpd.read_file("data/geoBoundaries-AGO-ADM1.geojson")

mapa = folium.Map(location=[-11.2027, 17.8739], zoom_start=6, width='100%', height='600px')

folium.GeoJson(
    provincias,
    name="Províncias",
    style_function=lambda x: {
        "fillColor": "#88cc88",
        "color": "green",
        "weight": 1,
        "fillOpacity": 0.3
    },
    tooltip=folium.GeoJsonTooltip(fields=["shapeName"], aliases=["Província:"]),
    popup=folium.GeoJsonPopup(
        fields=["shapeName"],
        aliases=[""],
        labels=False,
        localize=True,
        parse_html=True,
        style="background-color: white;",
        sticky=False
    )
).add_to(mapa)

for idx, row in provincias.iterrows():
    ponto = row.geometry.representative_point()
    nome_provincia = row["shapeName"]
    link = f"/provincia/{nome_provincia.replace(' ', '_')}"
    folium.Marker(
        location=[ponto.y, ponto.x],
        tooltip=nome_provincia,
        popup=f"<a href='{link}' target='_blank'>Ver mais sobre {nome_provincia}</a>",
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(mapa)

folium.LayerControl().add_to(mapa)

mapa.save("mapa.html")  # salva o mapa como HTML completo
