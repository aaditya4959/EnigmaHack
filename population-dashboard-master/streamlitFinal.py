###############################################################################################################################################
#                                                             Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px


###############################################################################################################################################
#                                                             Page configuration
st.set_page_config(
    page_title="Environmental Impact Assessment Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

###############################################################################################################################################
#                                                                  CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


###############################################################################################################################################
#                                                                 Load data
df_reshaped = pd.read_csv('data/Dataset.csv')


###############################################################################################################################################
#                                                                    Sidebar
with st.sidebar:
    st.title('🌍 Environmental Impact Assessment Dashboard')
    
    pr_list = list(df_reshaped.Project_Type.unique())[::-1]
    
    selected_pr = st.selectbox('Select a Project Type', pr_list)
    df_selected_pr = df_reshaped[df_reshaped.Project_Type == selected_pr]
    df_selected_pr_sorted = df_selected_pr.sort_values(by="Impact_Score", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


##############################################################################################################################################
#                                                             Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=600,height =300,
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme, hg=300, wd=700):
    choropleth = px.choropleth(input_df, 
                               locations=input_id, 
                               color=input_column, 
                               locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df[input_column])),
                               scope="usa",
                               labels={input_column: 'Impact Score'})
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=hg,
        width= wd
    )
    return choropleth


# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# # Convert population to text 
# def format_number(num):
#     if num > 1000000:
#         if not num % 1000000:
#             return f'{num // 1000000} M'
#         return f'{round(num / 1000000, 1)} M'
#     return f'{num // 1000} K'

# # Calculation year-over-year population migrations
# def calculate_Imp_difference(input_df, input_year):
#   selected_pr_data = input_df[input_df['Project_Type'] == input_year].reset_index()
#   previous_pr_data = input_df[input_df['Project_Type'] == input_year - 1].reset_index()
#   selected_pr_data['ImpactScore_difference'] = selected_pr_data.Impact_Score.sub(previous_pr_data.Impact_Score, fill_value=0)
#   return pd.concat([selected_pr_data.states, selected_pr_data.id, selected_pr_data.Impact_Score, selected_pr_data.ImpactScore_difference], axis=1).sort_values(by="ImpactScore_difference", ascending=False)


###############################################################################################################################################
#                                                      Dashboard Main Panel

col = st.columns((5, 3.5), gap='medium')
# col = st.columns((1.5, 4.5, 2), gap='medium')

# with col[0]:
#     # Dashboard - left side
#     st.markdown('#### Gains/Losses')
#     df_Impact_difference_sorted = calculate_Imp_difference(df_reshaped, selected_pr)

#     # Filter states with positive and negative impact
#     positive_states = df_Impact_difference_sorted[df_Impact_difference_sorted['ImpactScore_difference'] > 50]
#     negative_states = df_Impact_difference_sorted[df_Impact_difference_sorted['ImpactScore_difference'] < -50]

#     # Calculate the percentage of positive and negative impact states
#     percentage_positive = len(positive_states) / len(df_Impact_difference_sorted) * 100
#     percentage_negative = len(negative_states) / len(df_Impact_difference_sorted) * 100

#     # Create donut charts
#     positive_donut_chart = make_donut(percentage_positive, 'Positive Impact', 'green')
#     negative_donut_chart = make_donut(percentage_negative, 'Negative Impact', 'red')

#     # Display donut charts
#     st.write('Positive Impact')
#     st.altair_chart(positive_donut_chart)

#     st.write('Negative Impact')
#     st.altair_chart(negative_donut_chart)


with col[0]:
    # Additional visualizations can be added here, if needed
    st.markdown(f'#### {selected_pr} Impact Assessment')

    st.markdown('#### States Impact')

    if selected_pr:
        # Filter states based on selected project type
        choropleth = make_choropleth(df_selected_pr, 'States_Code', 'Impact_Score', selected_color_theme)
        st.plotly_chart(choropleth, use_container_width=True)

        heatmap = make_heatmap(df_reshaped, 'Project_Type', 'States', 'Impact_Score', selected_color_theme)
        st.altair_chart(heatmap, use_container_width=True)
    


with col[1]:
    st.markdown('#### States for Selected Project Type')

    st.dataframe(df_selected_pr_sorted,
                 column_order=("States", "Impact_Score"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "States": st.column_config.TextColumn(
                        "States",
                    ),
                    "Impact_Score": st.column_config.ProgressColumn(
                        "Impact Score",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_pr_sorted.Impact_Score),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - :orange[**Positive / Negative Impact Score**]: Positive and Negative Impact on the environment.
            - :orange[**Impact Score**]: Impact Score calculated by considering factors like Air_Emissions, Water_Pollution, Habitat_Loss, Carbon_Footprint etc.
            ''')

