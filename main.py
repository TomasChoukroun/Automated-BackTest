import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from dateutil.relativedelta import relativedelta
import scipy.optimize

def xlookup(lookup_value, lookup_array, return_array, if_not_found:str = ''):
    match_value = return_array.loc[lookup_array == lookup_value]
    if match_value.empty:
        return 0 if if_not_found == '' else if_not_found
    else:
        return match_value.tolist()[0]

def xnpv(rate, values, dates):
    if rate <= -1.0:
        return float('inf')
    d0 = dates[0]  # or min(dates)
    return sum([vi / (1.0 + rate) ** ((di - d0).days / 365.0) for vi, di in zip(values, dates)])

def xirr(values, dates):
    try:
        return scipy.optimize.newton(lambda r: xnpv(r, values, dates), 0.0)
    except RuntimeError:    # Failed to converge?
        return scipy.optimize.brentq(lambda r: xnpv(r, values, dates), -1.0, 1e10)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

# Excel Import
df = http://pd.read_excel('Enter Sheet Name Here', sheet_name='PYTHON 3')
Prices = df['Price'].tolist()
Dates = df['Date'].tolist()

# Collumn Arrays and Modelling
arr1 = np.array(Prices)
arr2 = np.array(Dates)
Nb_dates = len(Prices)

# M = int(input("Maturity (Months): "))
# PR = float(input("Participation Rate: "))
# Strike = float(input("Strike: "))

M = 36
PR = 1.3061
Strike = 1

dt = arr2[0] + relativedelta(months=M)
df7 = df.set_index('Date')
Maturity_Index = (df7.index.get_loc(dt, method='nearest'))

arr3 = Dates[Maturity_Index:-1]
Length_Maturity = len(arr3)
Dates_Out_Of_Scope = Nb_dates - Length_Maturity

df3 = pd.DataFrame(columns=['Maturity'])
List = []
for i in range(1, Dates_Out_Of_Scope+1):
    Extended_Date = arr3[-1] + relativedelta(days=i)
    List.append(Extended_Date)
df3['Maturity'] = List

df4 = pd.DataFrame(columns=['Maturity'])
df4.Maturity = arr3
dfinal = df4.append(df3, ignore_index=True)

# YYYY = int(input("Last Obs Year: "))
# M = int(input("Last Obs Month: "))
# D = int(input("Last Obs Day: "))
YYYY = 2022
M = 6
D = 16
Last_Obs_Date = pd.Timestamp(YYYY,M,D,0)
Last_Obs_Date1 = Last_Obs_Date.date()

df1 = pd.DataFrame(columns=['Dates', 'Prices'])
df1.Dates = df['Date']
df1.Prices = df['Price']
df1 = df1.join(dfinal['Maturity'])
df1['M1'] = df1['Maturity'].apply(xlookup, args = (df1['Dates'], df1['Prices']))
df1.insert(3, 'Last_Obs_Date', Last_Obs_Date1)
df1['BT_Ok'] = np.where((df1['Maturity'] < df1['Last_Obs_Date']),"TRUE","FALSE")
df1['Perf'] = np.where((df1['Maturity'] < df1['Last_Obs_Date']),(df1['M1']/df1['Prices']),0)
df1['Payoff'] = np.where((df1['Maturity'] < df1['Last_Obs_Date'])&(df1['Perf'] > 1), PR*(df1['Perf']-Strike), 0)
df1['CF Initial'] = np.where((df1['Maturity'] < df1['Last_Obs_Date']), -1, 0)
df1['CF Final'] = np.where((df1['Maturity'] < df1['Last_Obs_Date']), (df1['Payoff']+1), 0)

df5 = pd.DataFrame(columns=['Maturity'])
New_Dates = []
for i in range(Nb_dates):
    Fixed_Maturity = arr2[i] + relativedelta(months=36)
    New_Dates.append(Fixed_Maturity)
df5['Maturity'] = New_Dates

df6 = pd.DataFrame(columns=['IRR'])
IRR = []
for i in range(Nb_dates):
    irr1 = xirr([(df1['CF Initial'][i]), (df1['CF Final'][i])], [df1.Dates[i], df5['Maturity'][i]])
    irr1 = irr1 * (irr1>0) + 0
    IRR.append(irr1)
df6['IRR'] = IRR
df1 = df1.join(df6['IRR'])

End_Index = np.where(df1['Maturity'] == Last_Obs_Date)
End = End_Index[0][0]

print("\n")
print("Average Payoff: ", df1['Payoff'][0:End].mean()*100, "%")
print("Minimum Payoff: ", df1['Payoff'][0:End].min()*100, "%")
print("Maximum Payoff: ", df1['Payoff'][0:End].max()*100, "%")
print("\n")
print("Average IRR: ", df1["IRR"][0:End].mean()*100, "%")
print("Minimum IRR: ", df1["IRR"][0:End].min()*100, "%")
print("Maximum IRR: ", df1["IRR"][0:End].max()*100, "%")

# print(df1)

# x = ((df1.Prices[0]*df1['CF Final'][0])/df1['M1'][0])
#
# IRR = []
# for i in range(Nb_dates):
#     irr1 = xirr([(-1 * df1.Prices[i]), x*(df1['M1'][i])], [df1.Dates[i], df1['Maturity'][i]])
#     irr1 = irr1 * (irr1>0) + 0
#     IRR.append(irr1)
# df5['IRR'] = IRR
# df1 = df1.join(df5['IRR'])
