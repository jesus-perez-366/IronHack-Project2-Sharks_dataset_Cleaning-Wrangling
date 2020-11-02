import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class clean():


    def clean_col_names(name):

        name = name.replace('(Y/N)','')\
                    .lower()\
                    .strip()\
                    .replace(' ','_')\


        return name




    def get_month(row):

        case_number = str(row['case_number']).replace(',','.').replace('-','.')
        date = str(row['date']).lower()
        
        month_dict = {'jan' : 1,'feb' : 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 
                    'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
        
        
        pattern = r'\d{4}\.(\d{2})\.\d{2}'
        match = re.search(pattern, case_number)
        
        if match is not None:
            month = int(match.group(1))
            if month != 0 and month <= 12:
                return month
            else:
                pass
        
        
        pattern = r'([a-z]{3})\-\d{4}'
        match = re.search(pattern, date)
        if match is not None:
            month = month_dict.get(match.group(1))
            return month

        else:
            return np.NaN



    def clean_year(row):
        
        date = row['date']
        year = row['year']
        
        if year > 0:
            return int(year)
        else:
            if 'B.C.' in date:
                pattern = r'\d+'
                match = re.search(pattern, date)
                year = -int(match.group())
                return year

            else:
                pattern = r'\d{4}' #Looking for a year (4 digits)
                match = re.findall(pattern, date)
                if len(match) == 1:
                    return int(match[0])
                elif len(match) == 2: #if two values, returns the median

                    year = round((int(match[0]) + int(match[1])) / 2)
                    return int(year)
                elif len(match) == 3:
                    return 1945 #this is the only case 'Said to be 1941-1945, more likely 1945'
                else:
                    return 1939 #Before the war, and World War II are the cases left. Checked Before war case was filed after WorldwarII therefore it means WWII
                                #df_backup[(df_backup.Date == '"Before the war"') | (df_backup.Date == 'World War II')]


    def was_provoked(row):
        
        txt = row['type']
        
        if txt == 'Provoked':
            return 1
        elif (txt == 'Questionable') or (txt =='Sea Disaster'):
            return np.NaN
        else:
            return 0 #rest of cases are related to boats or classified as unprovoked


    def clean_fatal(fatal):
        fatal = str(fatal)
        fatal = fatal.lower()\
                    .strip()

        if fatal == 'y':
            return 1
        elif fatal == 'n':
            return 0

        else:
            return np.NaN

        

    def find_type_shark(txt):
    
        valid_type_sharks = ['white','tiger','bull','mako','sandbar','lemon','whitetip','blue','galapagos','dusky','blacktip',
                'silky','hammerhead','sevengill','sixgill','nurse','sand','carpet','wobbegong','basking','dog','spinner','whaler','sandtiger']
        
        valid_reef_sharks = ['whitetip','caribbean', 'grey', 'blacktip']


        txt = str(txt).lower()
        
        match = re.search(r'([a-z]{2,25})\sshark',txt)
        try:
            match_group = match.group()

        except AttributeError:
            return np.NaN
        
        else:
            
            if match_group.split()[0] in valid_type_sharks:
                shark_type = match.group().split()[0]
                return shark_type
            
            elif match.group().split()[0] == 'reef':
                match = re.search(r'([a-z]){2,25}\sreef\sshark',txt) 
                try:
                    type_reef = match.group(0).split()[0]
                    

                except AttributeError:
                    return 'reef'
                
                else:
                    if type_reef in valid_reef_sharks:
                        shark_type = type_reef + ' reef'
                        return shark_type
                    else:
                        return 'reef'
                    
            else:
                
                return np.NaN



class plot():

    my_palette = {'USA': sns.color_palette()[0], 'AUSTRALIA':sns.color_palette()[1]}

    def plot_cases(df, only_provoked = False):

        fig = plt.figure()
        ax = fig.add_subplot(111)


        if only_provoked:
            df = df[df.was_provoked == 0]
            plt.suptitle('Not Provoked cases')
            filename = 'img/countplot_provoked_cases.png'

        else:
            plt.suptitle('All cases: Provoked and not Provoked')
            filename = 'img/countplot_all_cases.png'

        sns.countplot(x = df.country, hue= df.was_fatal)
        ax.legend(labels = ['Not Fatal', 'Fatal'])
        plt.xlabel('') #To remove countries 
        plt.ylabel('Number of incidents') #To remove countries 
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        
        plt.title('In %, fatal cases overall')

        for pos, country in enumerate(df.country.unique()):
            
            fatal = df[(df.country == country) & (df.was_fatal == 1)].was_fatal.count()
            total_number = df[(df.country == country) & (pd.notnull(df.was_fatal))].was_fatal.count()
            number = round((fatal / total_number) * 100,1)

            plt.text(pos + 0.08, fatal + fatal * 0.1, f'{number} %',fontsize = 15, ha = 'left')


        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)

    def get_coordin(area, coordin):

        coordin_dict = {'Florida': (710,50), 'California': (45,245) , 'Hawaii': (375,40), 'South Carolina':(725,240) ,
                'North Carolina':(760,290) , 'Texas':(450,120) , 'New Jersey': (760,375),'Oregon':(15,510), 
                'New York': (780,410), 'Virginia': (750,345), 'New South Wales':(800,200) , 'Queensland': (750,450) ,
                        'Western Australia': (100,150) , 'South Australia':(420,170) , 'Victoria':(580,90) ,
                        'Torres Strait':(620,580) , 'Tasmania':(710,50) , 'Northern Territory': (450,580) }

        result = coordin_dict.get(area)[coordin]
        

        return result

        
    def plot_areas(df, country):

        if country == 'USA':
            top = 10
            path = 'img/US-MAP-CLEAN.png'
            filename = 'img/usa_map_cases.png'

        elif country == 'AUSTRALIA':
            top = 8
            path = 'img/aus_map-clean.png'
            filename = 'img/aus_map_cases.png'

        else:
            pass

        df_temp = pd.DataFrame(df[df.country == country].groupby('area').was_fatal.count()).reset_index() #to get total number of cases with info fatal included
        df_temp1 = pd.DataFrame(df[df.country == country].groupby('area').was_fatal.sum()).reset_index() #to get number of fatal cases
        df_temp = df_temp.merge(df_temp1, on='area').sort_values('was_fatal_x', ascending=False).head(top) #merge, sort and keep only top values

        #column was_fatal_x is total number of cases
        #column was_fatal_y is total number of fatal cases


        #To get coordinates to plot on map
        df_temp['x_axis'] = df_temp.area.apply(lambda x: plot.get_coordin(x,0)) 
        df_temp['y_axis'] = df_temp.area.apply(lambda x: plot.get_coordin(x,1))

        fig = plt.figure(figsize = (15, 10))
        ax = fig.add_subplot(111)
        img = plt.imread(path)
        ax.imshow(img, extent = [0, 900, 0, 600])

        factor = 9 #For determining size of point

        sns.scatterplot(x = df_temp.x_axis, y = df_temp.y_axis, s = df_temp.was_fatal_x * factor, color = 'orange') #This plots total number of cases
        sns.scatterplot(x = df_temp.x_axis, y = df_temp.y_axis, s = df_temp.was_fatal_y * factor, color = 'red') # This plots total number of fatal cases

        for place in df_temp.area.unique():

            interspace = 15
            fontsize = 15
            lateral_space = 5

    
            #plot number of total cases
            y = int(df_temp[df_temp.area == place].y_axis) #int to solve error
            value = int(df_temp[df_temp.area == place].was_fatal_x)

            circle_radius = (value * factor)**(1/2)/2
            x = int(df_temp[df_temp.area == place].x_axis) + circle_radius + lateral_space #5 for spacing
            plt.text(x, y, value, color = 'orange', fontsize = fontsize, ha='left')
            

            
            #plot number of fatal cases
            y = int(df_temp[df_temp.area == place].y_axis)- interspace
            value2 = int(df_temp[df_temp.area == place].was_fatal_y)
            x = int(df_temp[df_temp.area == place].x_axis) + circle_radius + lateral_space 
            plt.text(x, y, value2, color = 'red', fontsize = fontsize, ha='left')

        ax.spines['top'].set_visible(False)
        ax.yaxis.set_visible(False)
        ax.xaxis.set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.title('Total cases in yellow. Fatal cases in red')

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)
        


    def plot_season_trend(df):

        fig, ax = plt.subplots()

        sns.countplot(x = df.month, hue= df.country)
        months_in_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        ax.set_xticklabels(months_in_order)

        plt.xlabel('') #To remove countries 
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.yaxis.set_visible(False)
        plt.legend(loc = 'best')

        filename = 'img/season_plot.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)


    def plot_attack_years(df, initial_year = 1950, ending_year = 2019):

        fig, ax = plt.subplots()

        df_temp = df.fillna('no').groupby(['country','year']).month.count().reset_index() #fillna to count total values
        df_temp = df_temp[(df_temp.year >= initial_year) &(df_temp.year <= ending_year)]

        
        sns.lineplot(x = df_temp.year, y = df_temp.month, hue = df_temp.country, palette = plot.my_palette)

        plt.xlabel('') #To remove countries 
        plt.ylabel('Number of incidents') #To remove countries 
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.legend(title= '',loc='upper left')

        filename = 'img/trend_years_plot.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)


    def plot_species(df):

        df_temp = df.groupby(['country','species']).count().groupby('country').year.sum() # this counts total cases
        df_temp2 = df.groupby(['country','species']).count().sort_values('year', ascending = False)\
                                        .groupby('country').year.head(5).reset_index() # this counts top 5 per country

        df_temp2['total'] = 0
        for country in df.country.unique():
            df_temp2['total'] = np.where(df_temp2['country'] == country, df_temp[country], df_temp2['total']) #fill in with total value

        df_temp2['shark_perc'] = round((df_temp2.year / df_temp2.total) * 100, 1) #this column for shark percentage

        df_temp3 = pd.DataFrame()
        df_temp3['species_total'] = df.groupby(['country','species']).was_fatal.count() # this counts total cases
        df_temp3['total_fatal'] = df.groupby(['country','species']).was_fatal.sum() #this to count fatal cases
        df_temp3['rate_fatal'] = round(df_temp3['total_fatal'] / df_temp3['species_total'] * 100, 1) #this calculates rate of fatal
        df_temp3 = df_temp3.reset_index()
        new_df = df_temp2.merge(df_temp3, how = 'inner', left_on=['country', 'species'], right_on = ['country', 'species']) #this merges with previous df

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        sns.barplot(x = df_temp2.species, y = df_temp2.shark_perc, hue = df_temp2.country, palette = plot.my_palette) #this plots bar plot with shark percentage

        ax2 = ax.twinx() #this to share plot
        sns.lineplot(ax = ax2, x = new_df.species, y = new_df.rate_fatal, linewidth = 3, linestyle = 'dashed', hue = new_df.country, palette = plot.my_palette)

        ax2.grid(False) #to remove axis on the right

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.set_yticks([])
        ax2.yaxis.set_visible(False)
        ax.set_xlabel('') 
        ax.set_ylabel('%') 

        plt.title('Top 5 most common species')
        ax.legend(title = 'Rate of appearance',loc = 'upper right')
        ax2.legend(title = 'Rate of fatality', loc = 'center right')

        filename = 'img/top_species.png'

        plt.savefig(filename,bbox_inches='tight',pad_inches=0.2)

 





    




        
        

        







    