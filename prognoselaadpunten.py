import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import json
import folium
from streamlit_folium import folium_static
from folium import Choropleth, LayerControl

df_groei = pd.read_csv(r'groeiscenarios.csv', sep=';', decimal=',')
df_groei = df_groei.set_index('Scenario')
df_groei = df_groei.astype(int)
df = pd.read_csv(r'filter_outlook_personenautos_2024Q1.csv', sep=',', decimal='.')
df['Jaar'] = df['Jaar'].astype('Int64')
df = df.query("Jaar < 2031")
df = df.rename(columns={'bu_naam': 'buurtnaam'})

st. set_page_config(layout="wide") 

custom_html = """
<div class="banner">
    <img src="https://j4q4x9z4.rocketcdn.me/wp-content/uploads/2018/07/banner_EPM_laadpalen-kl.jpg" alt="Banner Image">
</div>
<style>
    .banner {
        width: 100%;
        height: 300px;
        overflow: hidden;
    }
    .banner img {
        width: 100%;
        height: auto;
        object-fit: cover;
    }
</style>
"""
# Display the custom HTML
st.components.v1.html(custom_html)


st.title("Data en visualisaties prognose laadpunten Ermelo, Harderwijk en Zeewolde")
st.write("###")
st.write("###")
st.write("###")
st.write("###")

gemeenten = ['Ermelo', 'Harderwijk', 'Zeewolde']
gemeente_keuze = st.sidebar.selectbox('Selecteer een gemeente:', gemeenten)
gefilterde_df = df[df['gemeente'] == gemeente_keuze]

laag = ['Jaar', 'buurtnaam', 'gemeente','aantal_evs_L', 'thuislaadpunten_L', 'publiekelaadpunten_L', 'werklaadpunten_L', 'snellaadpunten_L']
midden = ['Jaar', 'buurtnaam', 'gemeente', 'aantal_evs_M', 'thuislaadpunten_M', 'publiekelaadpunten_M', 'werklaadpunten_M', 'snellaadpunten_M']
hoog = ['Jaar', 'buurtnaam', 'gemeente', 'aantal_evs_H', 'thuislaadpunten_H', 'publiekelaadpunten_H', 'werklaadpunten_H', 'snellaadpunten_H']

scenario_keuze = st.sidebar.selectbox('Selecteer een scenario', ('laag', 'midden', 'hoog'))

scenario_kolommen = {
    'laag': laag,
    'midden': midden,
    'hoog': hoog
}

gefilterde_df = gefilterde_df[scenario_kolommen[scenario_keuze]]


te_wijzigen_indices = [3, 4, 5, 6, 7]

kolomnamen = gefilterde_df.columns.tolist()

for index in te_wijzigen_indices:
    kolomnamen[index] = kolomnamen[index][:-2]
gefilterde_df.columns = kolomnamen


data_EV = gefilterde_df.query("Jaar < 2031")
data_EV = data_EV[['Jaar', 'aantal_evs']]
data_EV = data_EV.rename(columns={'aantal_evs' : 'Aantal elektrische voertuigen'})
data_EV = data_EV.groupby('Jaar').sum().reset_index()
data_EV = data_EV.round(0)
data_EV['Jaar'] = data_EV['Jaar'].astype('Int64')
#data_EV = data_EV.set_index('Jaar')

data_ermelo_bar = gefilterde_df.query("Jaar < 2030")
data_ermelo_bar = data_ermelo_bar[['Jaar', 'thuislaadpunten', 'publiekelaadpunten', 'werklaadpunten', 'snellaadpunten']]
data_ermelo_bar = data_ermelo_bar.groupby('Jaar').sum().reset_index()
data_ermelo_bar = data_ermelo_bar.set_index('Jaar')
data_ermelo_bar = data_ermelo_bar.round(0)


waarde_EV_2023 = pd.to_numeric(data_EV['Aantal elektrische voertuigen'][0], errors='coerce')
waarde_EV_2030 = pd.to_numeric(data_EV['Aantal elektrische voertuigen'][7], errors='coerce')

# Bereken de groei in procenten
proc_groei = ((waarde_EV_2030 - waarde_EV_2023) / waarde_EV_2023) * 100
st.subheader('Elaad Prognosemodel Elektrische personen voertuigen (BEV)')

col1, col2 = st.columns(2)
with col2:
    st.write(f'Het aantal elektrische personenvoertuigen zal in de komende jaren flink stijgen. Waar er in de gemeente {gemeente_keuze} in 2023 nog {waarde_EV_2023:.0f} elektrische personevoertuigen waren, '
             f'Neemt dit aantal toe naar {waarde_EV_2030:.0f} in 2030; een groei van {proc_groei:.0f}%')
    fig1 = alt.Chart(data_EV, title=f'Figuur 1. Aantal elektrische personenvoertuigen {gemeente_keuze}, volgens het {scenario_keuze} scenario').mark_bar(size=50).encode(
        x =alt.X('Jaar:O', axis=alt.Axis(format='', title='Jaar')), 
        y='Aantal elektrische voertuigen'
    ).properties(
        width=600,  # Breedte van het figuur in pixels
        height=600   # Hoogte van het figuur in pixels
    )
    st.altair_chart(fig1, use_container_width=True)
    

with col1: 

    st.write("In de meest recente uitgave van de Elaad Outlook hebben onderzoekers de toekomstverwachtingen voor elektrische personenauto's en de daarvoor vereiste laadinfrastructuur herzien. "
             "Voor deze update hebben zij een grondige analyse uitgevoerd van de nieuwste ontwikkelingen in de markt en de nieuw beschikbare gegevens over elektrische voertuigen bestudeerd. "
             "Aan de hand hiervan zijn de verwachte groei en de verspreiding van elektrische auto's en de benodigde laadpunten verfijnd en geactualiseerd. ")
    st.write("Het model rekent met drie verschillende scenario's: 'Hoog', 'Midden' en 'Laag', waarbij het hoge scenario de sterkste groei in elektrische voertuigen en laadpalen voorspeld. "
             "De drie scenario's zijn gebasseerd op het jaartal waarin de instroom van nieuweverkopen en de instroom in het wagenpark 100% elektrisch zijn. "
             "De belangrijkste uitganspunten van de groeiscenario's zijn te zien in tabel 1. ")
    st.write("De overige, onderliggende annames per scenario staan omschreven in het [ElaadNL rapport](https://elaad.nl/wp-content/uploads/downloads/ElaadNL_Outlook_Personenautos_2024_def.pdf). ")
             
    st.dataframe(df_groei, use_container_width=True)
    st.write("In het bovenstaande selectievenster kun je kiezen voor één van de drie scenario's waarna de figuren worden geupdate. ")


st.write('###')
st.write('###')
st.write('###')
st.write('###')
st.write('###')

st.subheader(f'Elaad Prognosemodel aantal laadpunten gemeente {gemeente_keuze}')
st.write('In figuur 2 is de prognose voor het aantal laadpunten te zien. Het model maakt onderscheid tussen drie verchillende typen laadpunten:')
st.write('  1)  Thuislaadpunten ')
st.write('  2)  Werklaadpunten ')         
st.write('  3)  (semi)Publiekelaadpunten ')
st.write('  4)  Aantal DC snellaadpunten ')
st.write("In het selectievenster boven figuur 2 kun je type laadpunten in- of uitschakelen. ")         

# Multi-select widget voor het selecteren van kolommen
st.write("###")
st.write("###")
st.write("###")
selected_columns = st.multiselect('Selecteer het type laadpunten voor de prognose:',
                                options=gefilterde_df.columns.tolist(),  # Alle kolommen als opties
                                default=['Jaar', 'gemeente', 'thuislaadpunten', 'publiekelaadpunten', 'werklaadpunten', 'snellaadpunten'])  # Standaard alle kolommen geselecteerd


# Filter het DataFrame op basis van geselecteerde kolommen
# Zorg dat 'Jaar' altijd geselecteerd is, aangezien dit nodig is voor de x-as
filtered_data = gefilterde_df[selected_columns]
gefilterde_df = gefilterde_df.round(0)
filtered_data = filtered_data.round(0)

long_df = pd.melt(filtered_data, id_vars=['Jaar'], var_name='Categorie', value_name='Waarde')
chart = alt.Chart(long_df, title=f'Figuur 2. Aantal laadpunten {gemeente_keuze}, volgens het {scenario_keuze} scenario').mark_bar().encode(
    x='Jaar:N',
    y=alt.Y('sum(Waarde):Q', stack='zero', title='Aantal laadpunten'),
    color='Categorie:N'
).properties(
    width=1200,
    height=600
)

# Toon de chart in Streamlit
st.altair_chart(chart)
#st.bar_chart(filtered_data, use_container_width=True)

st.write('###')
st.write('###')
st.write('###')
st.write('###')
st.write('###')



df_2024 = gefilterde_df.query("Jaar == 2024")
df_2024 = df_2024.round(0)
df_2024 = df_2024.set_index('buurtnaam')
df_2030 = gefilterde_df.query("Jaar == 2030")
df_2030 = df_2030.round(0)
df_2030 = df_2030.set_index('buurtnaam')


st.subheader('Prognose laadpunten op buurtniveau')


col1, col2 = st.columns(2)

with col2:
    verschil_laadpunten = df_2030['publiekelaadpunten'] - df_2024['publiekelaadpunten']
    verschil_laadpunten = pd.DataFrame(verschil_laadpunten)
    verschil_laadpunten = verschil_laadpunten.rename(columns={'publiekelaadpunten': 'groei (semi)publiekelaadpunten 2024 - 2030'})
    verschil_laadpunten['groei (semi)publiekelaadpunten 2024 - 2030'] = pd.to_numeric(verschil_laadpunten['groei (semi)publiekelaadpunten 2024 - 2030'], errors='coerce')
    verschil_laadpunten_sorted = verschil_laadpunten.sort_values(by='groei (semi)publiekelaadpunten 2024 - 2030', ascending=True)
    fig = px.bar(verschil_laadpunten_sorted, x=verschil_laadpunten_sorted.index, y='groei (semi)publiekelaadpunten 2024 - 2030')

    #KAART
    import geopandas as gpd

    # Laad het GeoJSON-bestand
    gdf = gpd.read_file('aangepaste_buurt_2023.geojson')
    # Converteer de geometry kolom naar strings vóór de samenvoeging
    gdf['geometry_str'] = gdf['geometry'].astype(str)
    # Voer je analyse of bewerkingen uit
    merged_df_verschil = df.query("Jaar == 2030 & gemeente == @gemeente_keuze")
    merged_df_verschil = pd.merge(merged_df_verschil, verschil_laadpunten, on='buurtnaam', how='inner')
    # Zorg dat 'gdf' het GeoDataFrame is en 'merged_df_verschil' het pandas DataFrame
    # Merk op dat voor de merge de oorspronkelijke 'geometry' kolom gebruikt wordt, niet 'geometry_str'
    merged_gdf_geo = gpd.GeoDataFrame(pd.merge(gdf, merged_df_verschil, left_on='statcode', right_on='bu_code', how='inner'), geometry='geometry')
    # Als je de samengevoegde gegevens wilt tonen met de string-representatie van de geometrie, 
    # converteer dan de 'geometry' kolom opnieuw naar strings. Anders, sla deze stap over.
    merged_gdf_geo['geometry_str'] = merged_gdf_geo['geometry'].astype(str)
    merged_gdf_geo['groei (semi)publiekelaadpunten 2024 - 2030'] = pd.to_numeric(merged_gdf_geo['groei (semi)publiekelaadpunten 2024 - 2030'], errors='coerce')
    # Zorg ervoor dat je GeoDataFrame 'geometry' kolom in geojson formaat is
    gdf_json = merged_gdf_geo.to_crs(epsg=4326).__geo_interface__

    # Maak de interactieve kaart
    fig = px.choropleth(merged_gdf_geo,
                        geojson=gdf_json,
                        locations=merged_gdf_geo.index,
                        hover_name='statnaam',
                        color='groei (semi)publiekelaadpunten 2024 - 2030',
                        color_continuous_scale="YlOrBr",
                        range_color=(0, 12),
                        labels={'groei (semi)publiekelaadpunten 2024 - 2030':'Groei Laadpunten'}
                    )

    # Update de layout om een meer geschikte kaartprojectie en zoomniveau te kiezen
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_geos(
        projection_type="mercator",  # Pas aan afhankelijk van voorkeur
        fitbounds="locations"
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Toon de kaart in Streamlit
    st.plotly_chart(fig)
with col1:
        st.write("Er zit een groot verschil in de spreiding van de groei van laadpunten per buurt. In sommige buurten zal de groei in laadpunten niet of nauwelijks plaatsvinden, "
         f"terwijl in anderen buurten het aantal laadpunten met tientallen procenten zal toenemen. In figuur 4 is te de prognose voor het aantal laadpunten per buurt met een staafgrafiek te zien te zien. "
         f"In figuur 3 is te zien in welke buurten van {gemeente_keuze} "
         "de groei aan laadpunten het sterkst zal zijn. Hoe donkerder de kleur, hoe groter de groei van het aantal laadpunten tussen 2024 en 2043. In figuur 3 is alleen rekening gehouden met het aantal (semi)publieke laadpunten. ")

    

#Bereken het verschil in laadpunten tussen 2030 en 2024 voor elke buurt

buurten = gefilterde_df['buurtnaam'].unique().tolist()
buurt_keuze = st.selectbox('Selecteer een buurt:', buurten)
gefilterde_buurt_df = gefilterde_df[gefilterde_df['buurtnaam'] == buurt_keuze]

fig = px.bar(gefilterde_buurt_df, x='Jaar', y='publiekelaadpunten')
fig.update_traces()
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                        xaxis_tickangle=-45,
                        title_text='Figuur 3. Prognose aantal (semi)publieke laadpunten per buurt',
                        xaxis_title="Buurt",
                        yaxis_title= "Aantal laadpunten 2024-2030",
                        width=600,
                        height=600)
st.plotly_chart(fig)
