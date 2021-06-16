from bs4 import BeautifulSoup, Tag, NavigableString
import requests
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource

COUNTRIES_URL = 'https://www.worldometers.info/geography/alphabetical-list-of-countries/'
GDP_URL = 'https://www.worldometers.info/gdp/gdp-per-capita/'

def country_total(soup: BeautifulSoup) -> list:
     '''
     This function scrapes all the country names with Beautiful Soup and returns
     a list

     Argument: Beautiful soup
     Return: a list of strings (country names)

     '''
     countries = soup.find_all('tr')
     counter = 0
     total_countries = []
     for country in countries:
          if counter == 0: # don't add the first entry 
               counter += 1
          elif counter != 0:
               country_name = str(country.contents[3].text)
               total_countries.append(country_name)
     # print(len(total_countries)) #195
     return total_countries

response_countries = requests.get(COUNTRIES_URL)
html_countries = response_countries.content
soup_countries = BeautifulSoup(html_countries, 'html.parser')
all_countries = country_total(soup_countries) # list of all countries
print(f'The number of countries on Earth according to Wikipedia is {len(all_countries)}.')

response_GDP = requests.get(GDP_URL)
html_GDP = response_GDP.content
soup_GDP = BeautifulSoup(html_GDP, 'html.parser')

full_names = []
all_data = []
table = soup_GDP.find("tbody")
# print(table.contents[1].find('a').text)
for tr in table:
     my_tr = tr.find('a')
     if my_tr != -1:
          full_names.append(my_tr.text)
          # print(my_tr.text) # countries

     if isinstance(tr, NavigableString):
          continue
     if isinstance(tr, Tag):
          until_position = len(tr.contents[5].text)
          processed = str(tr.contents[5].text[1:until_position - 1])
          if processed != 'N.A.':
               all_data.append(processed)
          else:
               all_data.append(str(0))

print(f'The number of countires we have data for is {len(full_names)}.')
# print(all_data)
data = {'Country': full_names, 
        'GDP' : all_data}

# print(data)
# columns is selecting which part of dictionary to include, names have to be the same
df = pd.DataFrame(data, columns = ['Country', 'GDP'])  
df.to_csv('/Users/yimengwang/Documents/M2M/myproject/countries_webscraping/countryGDP_dataframe.csv', 
          index = False, header = True) #export as csv 

df.index += 1

# converting from dollar format to int for GDP data
df[df.columns[1]] = df[df.columns[1]].replace('[\$,]', '', regex=True).astype(int)

# graph top 10 countries
# since it is already in sorted list, it becomes easy to graph them
countries = df['Country'].tolist()[:9]
GDPs = df['GDP'].tolist()[:9]
source = ColumnDataSource(data=dict(countries=countries, GDPs=GDPs))
visual = figure(title="Top 10 Countries with GDP (PPP) Per Capital in 2017", x_range=countries, 
               y_range=(0,130000), x_axis_label = "Countries", y_axis_label = "GDP ($)", 
               plot_height = 500, plot_width = 800)

visual.vbar(x='countries', top='GDPs', width=0.8, source=source)
visual.xgrid.grid_line_color = None
show(visual)

# mean GDP calculation
mean_GDP = df['GDP'].mean()
print(f'The mean GDP of all countries is {mean_GDP}.')

# median_GDP calculation and finding the countries below median GDP value
median_GDP = df['GDP'].median()
print(f'The median GDP of all countries is {median_GDP}.')

less_than_median = df[(df.GDP < median_GDP)] 
less_than_median = less_than_median['Country']
print(less_than_median) # countries names with GDP less than median
