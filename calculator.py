import numpy as np
import pandas as pd
import math
import json
from pandas.io.json import json_normalize
from scipy.stats import norm
from helper import *

alpha = 1.4

# Supervisory factor for interest rates is 0.50%
SF_usd = 0.005
SF_gbp = 0.005

filename = input("Please enter name of the json file without ending: ")+".json"
content = get_content(filename)

# Parse json file into a pandas Dataframe
df = json_normalize(content["data"])

################
# Replacement Cost (unmargined trades only)
RC = max(sum(df["mtm_dirty"])/1000,0)

# Time bucket 
time_bucket = []

diff = ((pd.to_datetime(df["end_date"]) - pd.to_datetime(df["start_date"])).dt.days/365.25)

for i in diff:
	if i <=1:
		time_bucket.append(1)
	elif i<=5:
		time_bucket.append(2)
	else:
		time_bucket.append(3)

df["time_bucket"]=time_bucket

# Supervisory delta & maturity factor 
S = []
E = []
MF = []

trade_date = pd.to_datetime(df["trade_date"])
start_date = pd.to_datetime(df["start_date"])
end_date = pd.to_datetime(df["end_date"])


for index, row in df.iterrows():
	# start date
	if start_date[index] <= trade_date[index]:
		S.append(0)
	else:
		S.append(round((start_date[index]-trade_date[index]).days/365.25))
	# end date
	E.append(round((end_date[index]-start_date[index]).days/365.25))
	# maturity factor
	MF.append(maturity_factor(start_date[index],end_date[index],trade_date[index]))

df["S"] = S
df["E"] = E
df["maturity_factor"] = MF

# Supervisory duration
df["sd"] = df.apply(lambda x:supervisory_duration(x["S"],x["E"]),axis=1)

# Adjusted notional
df["adjusted_notional"] = (df["notional_amount"].multiply(df["sd"]))/1000

# Supervisory delta
supervisory_delta = []

for index, row in df.iterrows():
	if df["type"][index] == "vanilla_swap":
		if df["payment_type"][index] == "fixed" and df["receive_type"][index] == "floating":
			supervisory_delta.append(1)
		elif df["payment_type"][index] == "floating" and df["receive_type"][index] == "fixed":
			supervisory_delta.append(-1)
		else:
			# when it's basis rate swap (receive & pay floating), or receive & pay fixed
			supervisory_delta.append(1)
	elif df["type"][index] == "swaption":
		# following Example 1 in the reg text
		is_bought = True if df["mtm_dirty"][index] > 0 else False
		is_call = True if df["payment_type"][index] == "Fixed" else False
		price = 0.06
		strike = 0.05
		time = round((pd.to_datetime(df["start_date"][index]) - pd.to_datetime(df["trade_date"][index])).days/365.25)
		delta = option_delta(is_call,is_bought, price, strike,0.5, time)
		supervisory_delta.append(delta)
	else:
		raise ValueError("Only interest rate swap and swaptions are accepted for this calculator")

df["supervisory_delta"] = supervisory_delta

# Effective notional
Effective_Notional = []

currency = df.currency_code.unique()

for i in currency:
	D1 = df.loc[(df["currency_code"] == i) & (df["time_bucket"]==1),"adjusted_notional"]
	D2 = df.loc[(df["currency_code"] == i) & (df["time_bucket"]==2),"adjusted_notional"]
	D3 = df.loc[(df["currency_code"] == i) & (df["time_bucket"]==3),"adjusted_notional"]

	D1 = 0 if D1.empty else D1.iloc[0] * df.loc[(df["currency_code"] == i) & (df["time_bucket"]==1),"supervisory_delta"].iloc[0]
	D2 = 0 if D2.empty else D2.iloc[0] * df.loc[(df["currency_code"] == i) & (df["time_bucket"]==2),"supervisory_delta"].iloc[0]
	D3 = 0 if D3.empty else D3.iloc[0] * df.loc[(df["currency_code"] == i) & (df["time_bucket"]==3),"supervisory_delta"].iloc[0]

	en = effective_notional(D1,D2,D3)
	Effective_Notional.append(en)

# AddOn
AddOn = sum(Effective_Notional) * 0.005

# Multiplier
Floor = 0.005
V = sum(df[df["mtm_dirty"]>=0]["mtm_dirty"])/1000
C = sum(df[df["mtm_dirty"]<0]["mtm_dirty"])/1000

if (V - C >=0) and (V >= 0):
	multiplier = 1
else:
	multiplier = get_multiplier(Floor, V,C,AddOn)

# EAD
EAD = get_EAD(alpha,RC,multiplier,AddOn)
print("EAD for this file is : "+"{}".format(EAD))


#### Save the result to another dataframe
results = [(RC,Effective_Notional[0],Effective_Notional[1],AddOn,multiplier,EAD)]
result_cols = ["RC","Effective_Notional_1","Effective_Notional_2","AddOn","multiplier","EAD"]
df2 = pd.DataFrame(results,columns = result_cols)

####
# Write the results to excel file for audit trail purpose 
writer = pd.ExcelWriter("Output.xlsx")
df.to_excel(writer,"Input",index=False)
df2.to_excel(writer,"Result",index=False)
writer.save()

