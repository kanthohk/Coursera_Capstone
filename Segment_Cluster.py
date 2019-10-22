#!/usr/bin/env python
# coding: utf-8

# In[23]:


import pandas as pd
import requests
from bs4 import BeautifulSoup 


# In[24]:


URL = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
r = requests.get(URL)


# #### Step1: 
#     Use BeautifulSoup to work on webpage

# In[25]:


soup = BeautifulSoup(r.content, 'html5lib') 
#print(soup.prettify())


# #### Step2: 
#     Extract only the table that is needed

# In[26]:


table = soup.find('table', attrs = {'class':'wikitable sortable'}) 
#print(table.prettify())  


# #### Step3: 
#     Fetch the header row to create the dataframe

# In[5]:


cols=[]
for row in table.findAll('tr'):
    for headers in row.findAll('th'):
        cols.append(headers.text.rstrip("\n\r"))
        
cols


# #### Step4: 
#     Create a dataframe with the data from table

# In[6]:


df = pd.DataFrame(columns=cols)
row_data = []

for row in table.findAll('tr'):
    for data in row.findAll('td'):
        row_data.append(data.text.rstrip("\n\r"))
    if len(row_data)==3:
        df=df.append(pd.DataFrame([row_data], columns=cols), ignore_index = True)
    row_data = []

df.head(11)


# In[7]:


df.shape


# #### Step5: 
#     Only process the cells that have an assigned borough. Ignore cells with a borough that is Not assigned.

# In[8]:


df = df[df.Borough != 'Not assigned']
df.head()


# In[9]:


df.shape


# #### Step6:
#  More than one neighborhood can exist in one postal code area.  For example, in the table on the Wikipedia page, you will notice that M5A is listed twice and has two neighborhoods: Harbourfront and Regent Park.   These two rows will be combined into one row with the neighborhoods separated with a comma as shown in row 11 in the above table.

# In[10]:


df1=df.groupby(['Postcode'], as_index=False, sort=False)['Borough'].first()
df2=df.groupby(['Postcode'], as_index=False, sort=False)['Neighbourhood'].agg(lambda x: ', '.join(x.values))
df=pd.merge(df1, df2, on=["Postcode"], how="inner")
df.head()


# In[11]:


df.shape


# #### Step7: 
#     If a cell has a borough but a Not assigned neighborhood, then the neighborhood will be the same as the borough

# In[12]:


df['Neighbourhood'] = df.apply(lambda x: x['Borough'] if x['Neighbourhood'] == 'Not assigned' else x['Neighbourhood'], axis=1)
df.head()


# In[13]:


df.shape


# #### Step8: 
#     Import and get coordinates from geocoder

# In[14]:


#!conda install -c conda-forge geocoder --yes


# In[15]:


import geocoder 


# In[16]:


# Class definition to generate latitude and logitude for a given postal_code
def geo_loc(postal_code):
        # initialize your variable to None
    lat_lng_coords = None
    i=0
         # loop until you get the coordinates
    print(postal_code)
    while(lat_lng_coords is None):
        g = geocoder.google('{}, Toronto, Ontario'.format(postal_code))
        lat_lng_coords = g.latlng
        print("Queried Geocode :", i)
        i += 1
    return(lat_lng_coords)


# In[17]:


df['Latitude'] = df['Postcode'].apply(lambda x: (geo_loc(x))[0])
df['Longitude'] = df['Postcode'].apply(lambda x: (geo_loc(x))[1])


# #### Step9:
#     Get the coordinates from csv as the geocoder package is not responding

# In[18]:


coor_df = pd.read_csv("http://cocl.us/Geospatial_data")


# In[19]:


coor_df.head()


# In[20]:


coor_df.columns = ['Postcode', 'Latitude', 'Longitude']


# In[21]:


df = pd.merge(df, coor_df, on=["Postcode"], how="inner")


# In[22]:


df.head(11)


# In[ ]:




