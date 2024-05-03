"""
Name:       Wayne Chan
CS230:      Section 230-6
Data:       Massachusetts Crashes 2017
URL:        Link to your web application on Streamlit Cloud (if posted)
Description:
This project is a dashboard that includes a map of all the crashes in the data and they are pinpointed
it also has a sidebar which can pop out to choose the month and the city
it has a progress-type chart of what types of collision.
It also has a bar chart of all the collision by city and number of crashes per city.
Finally, it has a pie chart of the percentage of the overall collisions of the selected city and month.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar

# [ST4] Page design features (Sidebar)
st.set_page_config(page_title="Massachusetts Crash Reports", page_icon="😱", layout="wide", initial_sidebar_state="expanded")

df = pd.read_csv('/Users/waynechan/Library/CloudStorage/OneDrive-BentleyUniversity/Cs230/Code/Final Project/2017_Crashes_10000_sample.csv')

# [DA1] Cleaning or manipulating data/ Lambda
# [DA9] Adding a new column to a DataFrame
df['CRASH_DATE_TEXT'] = pd.to_datetime(df['CRASH_DATE_TEXT'], errors='coerce', infer_datetime_format=True)
df['month'] = df['CRASH_DATE_TEXT'].dt.month
df['month_name'] = df['month'].apply(lambda x: calendar.month_name[x] if pd.notna(x) else None)
df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
df = df.dropna(subset=['LAT', 'LON', 'CITY_TOWN_NAME', 'MANR_COLL_DESCR'])

# [DA2] Sorting data in ascending or descending order
months_sorted = ['All Months'] + sorted(df['month_name'].dropna().unique(), key=lambda x: list(calendar.month_name).index(x))

# [PY5] A dictionary accessing its keys, values, or items
plot_styles = {
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'font': {'color': 'black', 'size': 12},
    'xaxis': {
        'title': 'City',
        'title_font': {'size': 14},
        'tickfont': {'size': 12}
    },
    'yaxis': {
        'title': 'Number of Crashes',
        'title_font': {'size': 14},
        'tickfont': {'size': 12}
    },
    'margin': {'l': 10, 'r': 10, 't': 40, 'b': 100},
    'bargap': 0.15
}

# [PY1] A function with two or more parameters
# [PY2] A function that returns more than one value
# [PY4] A list comprehension
def filter_data(df, cities=['All of Massachusetts'], months=['All Months']):
    df_filtered = df.copy()
    if 'All of Massachusetts' not in cities:
        df_filtered = df_filtered[df['CITY_TOWN_NAME'].isin([city for city in cities])]
    if 'All Months' not in months:
        df_filtered = df_filtered[df_filtered['month_name'].isin([month for month in months])]

    num_crashes = len(df_filtered)
    unique_cities = df_filtered['CITY_TOWN_NAME'].nunique()
    return df_filtered, num_crashes, unique_cities

# [ST1], [ST2], [ST3] At least three Streamlit different widgets  (sliders, drop downs, multi-selects, text box, etc)
with st.sidebar:
    st.title('🚗💥🚙 Massachusetts Crash Reports')
    st.write("Data for Year: 2017")
    city_list = ['All of Massachusetts'] + sorted(df['CITY_TOWN_NAME'].unique())
    selected_city = st.multiselect('Select cities', city_list, default=['All of Massachusetts'])
    selected_months = st.multiselect('Select months', months_sorted, default=['All Months'])
    map_type = st.selectbox("Choose Map Type", ["Regular Map", "Heatmap"])

# [DA4] Filtering data by one condition
# [DA5] Filtering data by two or more conditions with AND or OR
df_filtered, num_crashes, unique_cities = filter_data(df, selected_city, selected_months)

left_column, center_column, right_column = st.columns([2, 3, 2])

# [VIZ1] charts with titles
# [VIZ2] charts with titles
# [PY5] Dictionary
with left_column:
    st.subheader("🤯Crash Data for Massachusetts🙊")
    top_cities = df_filtered['CITY_TOWN_NAME'].value_counts().nlargest(20).reset_index()
    top_cities.columns = ['City', 'Number of Crashes']
    bar_fig = px.bar(top_cities, x='City', y='Number of Crashes', title='🔝Top 20 Cities by Number of Crashes⬆️',
                     color='Number of Crashes', text='Number of Crashes', height=500,
                     color_continuous_scale=px.colors.sequential.Viridis)
    bar_fig.update_traces(textposition='outside')
    bar_fig.update_layout(**plot_styles)
    st.plotly_chart(bar_fig, use_container_width=True)
    percentage_fig = go.Figure(data=[go.Pie(labels=["Selected Crashes", "Other Crashes"],
                                            values=[num_crashes, len(df) - num_crashes],
                                            hole=.5, textinfo='label+percent')])
    percentage_fig.update_traces(textposition='inside', textinfo='percent')
    percentage_fig.update_layout(title='Percentage of Overall Crashes🥧', title_x=0.2, annotations=[
        dict(text=f'{num_crashes / len(df) * 100:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(percentage_fig, use_container_width=True)

# [VIZ3] charts with titles
# [VIZ4] At least one detailed map
with center_column:
    st.header(f"Map of Car Crashes in {', '.join(selected_city) if selected_city else 'Massachusetts'} for {', '.join(selected_months)}")
    if map_type == "Heatmap":
        heatmap_fig = px.density_mapbox(df_filtered, lat='LAT', lon='LON', radius=10,
                                        center=dict(lat=42.4072, lon=-71.3824), zoom=10,
                                        mapbox_style="stamen-terrain")
        st.plotly_chart(heatmap_fig, use_container_width=True)
    else:
        map_fig = px.scatter_mapbox(df_filtered, lat="LAT", lon="LON", hover_name="CITY_TOWN_NAME",
                                    zoom=10 if len(selected_city) == 1 and 'All of Massachusetts' not in selected_city else 8,
                                    mapbox_style="open-street-map", height=600)
        st.plotly_chart(map_fig, use_container_width=True)

# [DA8] Iterating through rows of a DataFrame with iterrows()
with right_column:
    st.subheader("😨Types of Collisions🙅")
    collision_counts = df_filtered['MANR_COLL_DESCR'].value_counts().reset_index()
    collision_counts.columns = ['Collision Type', 'Number of Crashes']
    max_crashes = collision_counts['Number of Crashes'].max()
    for _, row in collision_counts.iterrows():
        st.write(f"{row['Collision Type']}: {row['Number of Crashes']} crashes")
        st.progress(row['Number of Crashes'] / max_crashes)
