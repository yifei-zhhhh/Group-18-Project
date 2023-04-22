#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import altair as alt
import streamlit as st



# ## Wages

# Data: https://data.bls.gov/cew/apps/table_maker/v4/table_maker.htm#
# 如果打不开https://data.bls.gov/cew/apps/data_views/data_views.htm#tab=Tables
# 在下面18.One area, one industry, quarterly 选2019-2022 All Ownerships，我没找到下载键所以手动输入了loll
# 
# <img src='wages.png'>

# In[2]:


data = {'time': ['2019Q1', '2019Q2', '2019Q3', '2019Q4',
                '2020Q1', '2020Q2', '2020Q3', '2020Q4',
                '2021Q1', '2021Q2', '2021Q3', '2021Q4',
                '2022Q1', '2022Q2', '2022Q3'],
        'Average Weekly Wage': [1183, 1094, 1092, 1185, 1221, 
                                1188, 1172, 1339, 1288, 1241, 1250, 1418, 1374, 1292, 1334]}
wage = pd.DataFrame(data)
# wage


# In[3]:


wage['change'] = round((1183-1145)/1145*100,2) #2018Q4:1145
for i in range(1, len(wage)):
    wage['change'][i] = round((wage['Average Weekly Wage'][i]-wage['Average Weekly Wage'][i-1])\
    /wage['Average Weekly Wage'][i-1]*100,2)
# wage


# ## General Look on Real Gross Domestic Product and Related Measures: Percent Change from Preceding Period

# In[4]:


xls = pd.ExcelFile('gdp4q22_2nd.xlsx')
df1 = pd.read_excel(xls, 'Table 1', header=1)


# In[5]:


df = df1.set_index('Unnamed: 1').T
df.reset_index(inplace=True)


# In[6]:


df = df.drop(df.columns[[0]],axis = 1)
df = df.drop(df.index[[0,1,2,3]],axis = 0)
df.columns.values[0] = "year"
df.columns.values[1] = "quarter"
df['time'] = df['year'].astype(str)+df['quarter']


# In[7]:


consumption = df[['time', 'Gross domestic product (GDP)', 'Personal consumption expenditures',\
                 'Gross private domestic investment', 'Exports', 'Imports',\
                 'Government consumption expenditures and gross investment']]
consumption['time'] = consumption['time'].str[:6]


# In[8]:


dat = consumption.merge(wage[['time', 'change']], on='time', how='left')


# In[9]:


# dat


# In[10]:


dat_long = pd.melt(dat, id_vars='time', value_vars=['Gross domestic product (GDP)', \
                                                    'Personal consumption expenditures', \
                                                   'Gross private domestic investment',
                                                   'Exports', 'Imports', \
                                                    'Government consumption expenditures and gross investment',
                                                   'change'])


# In[11]:


variables=list(dat_long['variable'].unique())
variables = variables[:-1]

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select Measures: ')
)

colorCondition = alt.condition(selectQ, 'variable:N', alt.value('lightgray'))
opacityCondition = alt.condition(selectQ, alt.value(1), alt.value(0.4))

base = alt.Chart(dat_long).encode(
    x='time',
).properties(
    height=400,
    width=650
)

q_chart = base.transform_filter(
    alt.datum.variable != 'change'
).mark_line().encode(
    y=alt.Y('value:Q', title='Change on Measures (%)'),
    color='variable:O'
).add_selection(
    selectQ
).encode(
    color=colorCondition,
    opacity=opacityCondition
)

death_chart = base.transform_filter(
    alt.datum.variable == 'change'
).mark_line(color='purple').encode(
    y=alt.Y('value:Q', title='Change on Average Weekly Wage (%)', 
            axis=alt.Axis(titleColor='purple'), scale=alt.Scale(domain=[-80, 100]))
)

gdp=alt.layer(q_chart, death_chart).resolve_scale(
    y = 'independent', color='independent'
).properties(title='Percent Change From Preceding Period on GDP Measures and Average Weekly Wage')
# gdp


# ### Specific Look on Goods

# In[12]:


df2 = pd.read_excel(xls, 'Table 2', header=1)
df = df2.set_index('Unnamed: 1').T
df.reset_index(inplace=True)
df = df.drop(df.columns[[0]],axis = 1)
df = df.drop(df.index[[0,1,2,3]],axis = 0)
df.columns.values[0] = "year"
df.columns.values[1] = "quarter"
df['time'] = df['year'].astype(str)+df['quarter']
df['time'] = df['time'].str[:6]


# In[13]:


goods = df[['Durable goods', 'Motor vehicles and parts', 'Furnishings and durable household equipment',
                     'Recreational goods and vehicles',\
                 'Other durable goods', 'Nondurable goods', 'Food and beverages purchased for off-premises consumption', \
                     'Clothing and footwear', 
                'Gasoline and other energy goods', 'Other nondurable goods', 'time']]
goods = goods.merge(wage[['time', 'change']], on='time', how='left')


# In[14]:


goods_long = pd.melt(goods, id_vars='time', value_vars=['Durable goods', 'Motor vehicles and parts', 'Furnishings and durable household equipment',
                     'Recreational goods and vehicles',\
                 'Other durable goods', 'Nondurable goods', 'Food and beverages purchased for off-premises consumption', \
                      'Clothing and footwear', 
                'Gasoline and other energy goods', 'Other nondurable goods', 'change'])


# In[15]:


goods_long['type'] = 'Durable'
for i in range(len(goods_long)):
    if goods_long['variable'][i] in ('Nondurable goods',
                                     'Food and beverages purchased for off-premises consumption', \
                     'Imports', 'Clothing and footwear', 
                'Gasoline and other energy goods', 'Other nondurable goods'):
        goods_long['type'][i] = 'Nondurable'
    elif goods_long['variable'][i] == 'change':
        goods_long['type'][i] = 'Wage'


# In[16]:


durable = goods_long[(goods_long['type'] == 'Durable') | (goods_long['type'] == 'Wage')]
variables=list(durable['variable'].unique())
variables = variables[:-1][1:]

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select durable goods: ')
)

colorCondition = alt.condition(selectQ, 'variable:N', alt.value('lightgray'))


base = alt.Chart(durable).encode(
    x='time',
).properties(
    height=400,
    width=500
)

goods_chart = base.transform_filter(
    alt.datum.variable =='Durable goods'
).mark_line(color='red').encode(
    y=alt.Y('value:Q', 
            scale=alt.Scale(domain=[-8, 16]),
))

death_chart = base.transform_filter(
    alt.datum.variable == 'change'
).mark_line(color='gray').encode(
    y=alt.Y('value:Q', title='Average Weekly Wage (%)',
           axis=alt.Axis(titleColor='gray')),
)

bar_d = base.transform_filter(
    (alt.datum.variable !='Durable goods')
    &(alt.datum.variable !='change')
).mark_bar().encode(
    y=alt.Y('value:Q', title='Durable Goods (%)', axis=alt.Axis(titleColor='red')),
    color='type:O'
).add_selection(selectQ).transform_filter(selectQ)

durable_line = alt.layer(bar_d+goods_chart, death_chart).resolve_scale(
    y = 'independent'
).properties(title='Durable Goods')


# In[17]:


nondurable = goods_long[(goods_long['type'] == 'Nondurable') | (goods_long['type'] == 'Wage')]
variables=list(nondurable['variable'].unique())
variables = variables[:-1][1:]

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select nondurable goods: ')
)

base = alt.Chart(nondurable).encode(
    x='time',
).properties(
    height=400,
    width=500
)

goods_chart2 = base.transform_filter(
    alt.datum.variable =='Nondurable goods'
).mark_line(color='red').encode(
    y=alt.Y('value:Q',
           scale=alt.Scale(domain=[-8, 16])
))

death_chart = base.transform_filter(
    alt.datum.variable == 'change'
).mark_line(color='gray').encode(
    y=alt.Y('value:Q',  title='Average Weekly Wage (%)',
           axis=alt.Axis(titleColor='gray'))
)

bar_n = base.transform_filter(
    (alt.datum.variable !='Nondurable goods')
    &(alt.datum.variable !='change')
).mark_bar().encode(
    y=alt.Y('value:Q', title='Nondurable Goods(%)', axis=alt.Axis(titleColor='red')),
    color='type:O'
).add_selection(selectQ).transform_filter(selectQ)

nondurable_line = alt.layer(bar_n+goods_chart2, death_chart).resolve_scale(
    y = 'independent'
).properties(title='Nondurable Goods')

# (durable_line|nondurable_line).properties(
#     title=alt.TitleParams(
#         text="Goods'Contributions to Percent Change in Real GDP",
#         anchor='middle')
# )


# ### Services

# In[18]:


services = df[['Household consumption expenditures (for services)', 'Housing and utilities', 'Health care',
                     'Transportation services',\
                 'Recreation services', 'Food services and accommodations', 'Financial services and insurance', \
                     'Other services', 'time']]
df['time'] = df['time'].str[:6]
services = services.merge(wage[['time', 'change']], on='time', how='left')
services_long = pd.melt(services, id_vars='time', value_vars=['Household consumption expenditures (for services)', \
                                                              'Housing and utilities', 'Health care',
                     'Transportation services',\
                 'Recreation services', 'Food services and accommodations', 'Financial services and insurance', \
                     'Other services', 'change'])


# In[19]:


variables=list(services_long['variable'].unique())
variables = variables[:-1][1:]

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select services: ')
)


base = alt.Chart(services_long).encode(
    x='time',
).properties(
    height=400,
    width=500
)

service_chart = base.transform_filter(
    alt.datum.variable =='Household consumption expenditures (for services)'
).mark_line(color='red').encode(
    y=alt.Y('value:Q'),
)

death_chart = base.transform_filter(
    alt.datum.variable == 'change'
).mark_line(color='gray').encode(
    y=alt.Y('value:Q', title='Average Weekly Wage (%)',
           axis=alt.Axis(titleColor='gray'), scale=alt.Scale(domain=[-25, 20]))
)

bar_s = base.transform_filter(
    (alt.datum.variable !='Household consumption expenditures (for services)')
    &(alt.datum.variable !='change')
).mark_bar().encode(
    y=alt.Y('value:Q', title='Household consumption expenditures (for services)(%)',
           axis=alt.Axis(titleColor='red')),
).add_selection(selectQ).transform_filter(selectQ)

service=alt.layer(bar_s+service_chart, death_chart).resolve_scale(
    y = 'independent'
).properties(title="Services' Contributions to Percent Change in Real GDP")
# service


# ### With Wages

# In[20]:


# service|gdp


# In[21]:


# (durable_line|nondurable_line).properties(
#     title=alt.TitleParams(
#         text="Goods'Contributions to Percent Change in Real GDP",
#         anchor='middle')
# )


# ## Without Wages

# In[22]:


durable = goods_long[(goods_long['type'] == 'Durable') | (goods_long['type'] == 'Wage')]
variables=list(durable['variable'].unique())
variables = variables[:-1][1:]

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select durable goods: ')
)

colorCondition = alt.condition(selectQ, 'variable:N', alt.value('lightgray'))


base = alt.Chart(durable).encode(
    x='time',
).properties(
    height=400,
    width=500
)

goods_chart = base.transform_filter(
    alt.datum.variable =='Durable goods'
).mark_line(color='red').encode(
    y=alt.Y('value:Q', 
#             scale=alt.Scale(domain=[-8, 16])
))

bar_d = base.transform_filter(
    (alt.datum.variable !='Durable goods')
    &(alt.datum.variable !='change')
).mark_bar().encode(
    y=alt.Y('value:Q', title='Durable Goods (%)'),
    color='type:O'
).add_selection(selectQ).transform_filter(selectQ)

d = (bar_d+goods_chart).properties(title='Durable Goods')


# In[23]:


nondurable = goods_long[(goods_long['type'] == 'Nondurable') | (goods_long['type'] == 'Wage')]
variables=list(nondurable['variable'].unique())
variables = variables[:-1][1:]
nondurable['line_label'] = len(nondurable) * ['overall contribution']

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select nondurable goods: ')
)

base = alt.Chart(nondurable).encode(
    x='time',
).properties(
    height=400,
    width=500
)

goods_chart2 = base.transform_filter(
    alt.datum.variable =='Nondurable goods'
).mark_line(color='red').encode(
    y=alt.Y('value:Q',
#            scale=alt.Scale(domain=[-8, 16])
),
opacity='line_label')

bar_n = base.transform_filter(
    (alt.datum.variable !='Nondurable goods')
    &(alt.datum.variable !='change')
).mark_bar().encode(
    y=alt.Y('value:Q', title='Nondurable Goods(%)'),
    color='type:O'
).add_selection(selectQ).transform_filter(selectQ)

nd = (bar_n+goods_chart2).properties(title='Nondurable Goods')


# In[53]:


goods = (d|nd).properties(
    title=alt.TitleParams(
        text="Goods' Contributions to Percent Change in Real GDP",
        anchor='middle')
)


# In[54]:


variables=list(services_long['variable'].unique())
variables = variables[:-1][1:]
services_long['line_label'] = len(services_long) * ['overall contribution']

selectQ=alt.selection_single(
    fields=['variable'],
    init={'variable':variables[0]},
    bind=alt.binding_select(options=variables,name='Select services: ')
)


base = alt.Chart(services_long).encode(
    x='time',
).properties(
    height=400,
    width=500
)

service_chart = base.transform_filter(
    alt.datum.variable =='Household consumption expenditures (for services)'
).mark_line(color='red').encode(
    y=alt.Y('value:Q', scale=alt.Scale(domain=[-25,25])),
    opacity='line_label',
).properties(title="Services' Contributions to Percent Change in Real GDP")

bar_s = base.transform_filter(
    (alt.datum.variable !='Household consumption expenditures (for services)')
    &(alt.datum.variable !='change')
).mark_bar().encode(
    y=alt.Y('value:Q', title='Household consumption expenditures (for services)(%)'),
).add_selection(selectQ).transform_filter(selectQ)

service2 = (bar_s+service_chart)


## visual1

from PIL import Image

image = Image.open('visual1.png')


#st.subheader("👁️ Views")
st.title("Global Commodity Price Change During the Covid-19")
st.write("The visualization below shows the overall commodity price change (estimated by all commodity price index) from 2019 to 2023. The time range contains the period before and after the pandemic for comparison. The change of Covid-19 new cases during the pandemic is also shown below.")
st.write("To be more specific, the top 10 commodities that had the largest price increase and decrease are shown on the left.")



st.image(image, width=1000, output_format = 'PNG')

## visual2

# In[26]:


st.title("Percent Change of GDP measures and Average Weekly Wage Quarterly Since 2019 to 2022")
st.write("The visualization below shows the percent change of real GDP versus the average weekly wage.")
st.write("Additionally, the users could select GDP's related measure through the dropdown box to make comparisons with the change of wage.")


# In[27]:


gdp


# In[28]:


# goods
st.write("To further investigate the influence on personal consumption expenditures, we visualize the contributions of goods and services to percent change in real GDP.")
st.write("The line in each plot shows the overall contributions, while the users could look at the specific contribution of a particular good or service through the bar plot by using the dropdown selection.")
goods


# In[29]:


service2


# In[ ]:
st.title("Household Expenditure Composition from 2018 to 2021")
st.write("The visualization below shows the yearly change of 10 categories of household expenditure, along with the subcategory change of 6 of them")


data1 = pd.DataFrame({
    "category": ["Apparel and services","Cash contribution","Education","Entertainment","Food","Healthcare","Housing","Miscellaneous","Personal insurance and persions","Transportation",
                 "Apparel and services","Cash contribution","Education","Entertainment","Food","Healthcare","Housing","Miscellaneous","Personal insurance and persions","Transportation",
                 "Apparel and services","Cash contribution","Education","Entertainment","Food","Healthcare","Housing","Miscellaneous","Personal insurance and persions","Transportation",
                 "Apparel and services","Cash contribution","Education","Entertainment","Food","Healthcare","Housing","Miscellaneous","Personal insurance and persions","Transportation"],
    "year":["2021","2021","2021","2021","2021","2021","2021","2021","2021","2021",
            "2020","2020","2020","2020","2020","2020","2020","2020","2020","2020",
            "2019","2019","2019","2019","2019","2019","2019","2019","2019","2019",
            "2018","2018","2018","2018","2018","2018","2018","2018","2018","2018"],
    "value":[233952,322566,163787,476379,1105178,728228,3021905,131738,1051819,1464325,
             188417,299564,166865,382340,961333,679445,2809933,119029,950893,1289479,
             248692,263854,190849,408392,1078750,686691,2734285,118856,947479,1420566,
             244915,248127,184932,423720,1039471,652982,2640250,130555,958921,1282692],
    "percentage":[0.026891414671724668,0.03707707591728021,0.018826358119775715,0.05475698104697342,0.12703375001738532,0.08370555123940258,0.3473503131136222,0.015142512934378268,0.12090044491433614,0.1683155980251215,
0.024010430086891056,0.03817415879962759,0.0212640070505797,0.048722502955794465,0.12250496922635026,0.08658330548935443,0.3580764997072878,0.015168150871803263,0.12117457499383864,0.1643214008184728,
0.030708728894324248,0.03258094733116879,0.023566219262191337,0.050428639484224935,0.1332050942320311,0.08479326939818092,0.3376321585930282,0.014676453932831787,0.11699562408145595,0.1754128647905627,
0.0313729534052429,0.031784401974491984,0.023689292281560456,0.05427739345025629,0.13315344200682375,0.08364523961563121,0.3382089305603681,0.01672374469436942,0.1228352034473549,0.16430939856390103
    ]
})
data2= pd.DataFrame({
    "categoryy":["Apparel and services","Apparel and services","Apparel and services","Apparel and services","Apparel and services",
                 "Food","Food","Food",
                 "Housing","Housing","Housing","Housing","Housing",
                 "Transportation","Transportation","Transportation","Transportation",
                 "Healthcare","Healthcare","Healthcare","Healthcare",
                 "Entertainment","Entertainment","Entertainment","Entertainment",
                 "Apparel and services", "Apparel and services", "Apparel and services", "Apparel and services","Apparel and services",
                 "Food", "Food", "Food",
                 "Housing", "Housing", "Housing", "Housing", "Housing",
                 "Transportation", "Transportation", "Transportation","Transportation",
                 "Healthcare", "Healthcare", "Healthcare", "Healthcare",
                 "Entertainment", "Entertainment", "Entertainment", "Entertainment",
"Apparel and services", "Apparel and services", "Apparel and services", "Apparel and services","Apparel and services",
                 "Food", "Food", "Food",
                 "Housing", "Housing", "Housing", "Housing", "Housing",
                 "Transportation", "Transportation", "Transportation","Transportation",
                 "Healthcare", "Healthcare", "Healthcare", "Healthcare",
                 "Entertainment", "Entertainment", "Entertainment", "Entertainment",
"Apparel and services", "Apparel and services", "Apparel and services", "Apparel and services","Apparel and services",
                 "Food", "Food", "Food",
                 "Housing", "Housing", "Housing", "Housing", "Housing",
                 "Transportation", "Transportation", "Transportation","Transportation",
                 "Healthcare", "Healthcare", "Healthcare", "Healthcare",
                 "Entertainment", "Entertainment", "Entertainment", "Entertainment"
                 ],
    "subcategory":["Men and boys","Women and girls","Children under 2","Footwear","Other apparel products and services",
                   "Food at home","Food away from home","Alcoholic beverage",
                   "Shelter","Utilities,fuels,and public services","Household operations","Housekeeping supplies","Household furnishings and equipment",
                   "Vehicle purchases","Gasoline, other fuels and motor oil","Other vehicle expenses","Public and other transportation",
                   "Health insurance","Medical services","Drugs","Medical supplies",
                   "Fees and admissions","Audio and visual equipment and services","Pets,toys,hobbies","Other entertainment supplies",
                   "Men and boys","Women and girls","Children under 2","Footwear","Other apparel products and services",
                   "Food at home","Food away from home","Alcoholic beverage",
                   "Shelter","Utilities,fuels,and public services","Household operations","Housekeeping supplies","Household furnishings and equipment",
                   "Vehicle purchases","Gasoline, other fuels and motor oil","Other vehicle expenses","Public and other transportation",
                   "Health insurance","Medical services","Drugs","Medical supplies",
                   "Fees and admissions","Audio and visual equipment and services","Pets,toys,hobbies","Other entertainment supplies",
                   "Men and boys","Women and girls","Children under 2","Footwear","Other apparel products and services",
                   "Food at home","Food away from home","Alcoholic beverage",
                   "Shelter","Utilities,fuels,and public services","Household operations","Housekeeping supplies","Household furnishings and equipment",
                   "Vehicle purchases","Gasoline, other fuels and motor oil","Other vehicle expenses","Public and other transportation",
                   "Health insurance","Medical services","Drugs","Medical supplies",
                   "Fees and admissions","Audio and visual equipment and services","Pets,toys,hobbies","Other entertainment supplies",
                   "Men and boys","Women and girls","Children under 2","Footwear","Other apparel products and services",
                   "Food at home","Food away from home","Alcoholic beverage",
                   "Shelter","Utilities,fuels,and public services","Household operations","Housekeeping supplies","Household furnishings and equipment",
                   "Vehicle purchases","Gasoline, other fuels and motor oil","Other vehicle expenses","Public and other transportation",
                   "Health insurance","Medical services","Drugs","Medical supplies",
                   "Fees and admissions","Audio and visual equipment and services","Pets,toys,hobbies","Other entertainment supplies",
                   ],
    "year":["2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021","2021",
            "2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020","2020",
            "2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019","2019",
            "2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018","2018"],
    "subvalue":[56507,87858,8844,44801,35942,
                701087,404091,73841,
                1771197,564237,218873,107042,360556,
                645014,286902,472093,60316,
                494784,142902,66401,24141,
                87296,136305,129294,123484,
                42869,71603,8918,41252,23775,
                649324,312009,62801,
                1654047,545665,192203,109917,308101,
                593602,205806,455490,34580,
                481223,113387,62556,22279,
                55723,137719,112904,75994,
                59093,92986,9966,55289,31357,
                613097,465653,76493,
                1612057,536253,207591,101081,277303,
                581033,276931,469390,103212,
                466729,130142,64211,25610,
                116302,132230,108457,51404,
                55134,99043,10242,51372,29124,
                585605,453865,76468,
                1544072,532153,200080,98029,265917,
                522435,277165,375532,107561,
                447507,119426,63492,22556,
                100636,135311,107134,80639
                ],
    "percentage":[0.035373358267374096,0.47761372531964863,0.048077759415499695,0.2435472297120988,0.1953879272853788,
0.5946358794896435,0.3427349347211538,0.06262918578920272,
0.5861193518657932,0.18671566445669205,0.07242881559810782,0.03542202683406659,0.11931414124534027,
0.4404855479487136,0.19592781657077493,0.32239632595223056,0.04119030952828095,
0.6794355613901141,0.19623249861307174,0.09118160795794723,0.03315033203886695,
0.1832490517004318,0.2861272222327181,0.27140994880126956,0.25921377726558054,
0.2275219327343074,0.380024095490322,0.04733118561488613,0.2189399045733665,0.12618288158711793,
0.6340225009617882,0.30465642191353864,0.06132107712467314,
0.588642860879601,0.19419146292811965,0.0684012750481951,0.03911730279689943,0.1096470983471848,
0.4603428674238723,0.15960411887601028,0.35323596059800944,0.026817053102107986,
0.7082589466402726,0.16688179322829663,0.09206926241270448,0.032789997718726316,
0.14574200972956008,0.36020034524245437,0.29529737929591465,0.19876026573207092,
0.23761615820435802,0.3739017495606998,0.04007382655584641,0.22232006787539557,0.12608819780370017,
0.5307082579162998,0.403077967146306,0.06621377493739412,
0.5895716796164262,0.1961218380673558,0.07592149318743291,0.03696798248902364,0.1014170066397614,
0.4061560249579537,0.19358142161913536,0.32811488599617217,0.07214766742673878,
0.6796773517093544,0.189520192458919,0.09350771524934032,0.03729474058238628,
0.2847796117955009,0.32378125971796773,0.2655701738276611,0.12586895465887024,
0.22511483575934507,0.40439744401118755,0.04181859012310393,0.20975440458934733,0.11891472551701611,
0.5247648166833642,0.40671166319275803,0.06852352012387784,
0.5848201553564415,0.20155394316676709,0.07578067388289977,0.037128666933560484,0.10071656066033116,
0.4072954323442944,0.21608054304498425,0.2927684176962063,0.083855606914515,
0.6853292821690065,0.1828935298270547,0.09723406959773714,0.03454311840620171,
0.23750590012272255,0.31934060228452754,0.2528414991031813,0.1903119984895686
    ]
})

categoryy_dropdown = alt.binding_select(options=["Apparel and services","Entertainment","Food","Healthcare","Housing","Transportation"],name="Select Subcategory:")
categoryy_select = alt.selection_single(fields=['categoryy'], bind=categoryy_dropdown,init={'categoryy': 'Housing'})
year_radio = alt.binding_radio(options=["2018","2019","2020","2021"] ,name="Select Year: ")
year_select = alt.selection_single(fields=['year'], bind=year_radio,init={'year': '2021'})
chart1 = alt.Chart(data2).mark_bar(size=50).encode(
    alt.X("subvalue:Q",title="Subcategory Expenditure(million dollars)"),
    color="subcategory:N",
    tooltip = [
        alt.Tooltip('subcategory', title='Subcategory: '),
        alt.Tooltip('subvalue', title='Expenditure: '),
    alt.Tooltip('percentage',title='Percentage: ',format='.2%')]
)

rightt=chart1.add_selection(
    categoryy_select
).transform_filter(
    categoryy_select
).add_selection(
    year_select
).transform_filter(year_select)


donut_chart=alt.Chart(data1).mark_arc(innerRadius=50).encode(
    theta="value:Q",
    color="category:N",
    tooltip=[
        alt.Tooltip('category', title='Category: '),
        alt.Tooltip('value', title='Expenditure: '),
        alt.Tooltip('percentage',title='Percentage: ',format='.2%')]
)




leftt= donut_chart.add_selection(
    year_select
).transform_filter(year_select)

household_expenditure=(leftt|rightt).resolve_scale(
    color='independent'
).configure_view(
    stroke=None
).configure_legend(
titleFontSize=18,
labelFontSize=15,
labelLimit=1000
).properties(title={
        "text": "Household Expenditure Composition 2018-2021",
        "anchor": "middle",
        "fontSize": 20,
        "offset": 40
    })
household_expenditure





