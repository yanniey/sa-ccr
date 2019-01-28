import numpy as np
import pandas as pd
import math
import json
from pandas.io.json import json_normalize
from scipy.stats import norm


def get_content(filename):
	with open(filename) as f:
		content = json.load(f)
	return content


def maturity_factor(start_date,end_date,trade_date):
	remaining_maturity = ((end_date - trade_date).days)/365.25
	# maturity factor is 1 for all unmargined trades whose remaining maturity is > 1 year
	if remaining_maturity >1:
		return 1
	# transaction remaining maturity is floored by 10 business days
	elif remaining_maturity < (10/365):
		return (10/365)
	else:
		return math.sqrt((min(remaining_maturity,1))/1)

def supervisory_duration(S,E):
	return (math.exp(-0.05*S) - math.exp(-0.05*E))/0.05

def option_delta(is_call,is_bought,price,strike,sigma, time):
	delta = (math.log(price/strike)+0.5*(sigma** 2)* time)/(sigma * math.sqrt(time))
	flip = 1 if is_bought else -1
	if is_call:
		return flip * norm.cdf(delta)
	else:
		return flip * -norm.cdf(-delta) 

def effective_notional(D1,D2,D3):
	return math.sqrt(D1**2+D2**2+D3**2+1.4*D1*D2+1.4*D2*D3+0.6*D1*D3)

def get_multiplier(Floor,V,C,AddOn):
	multiplier = math.exp((V-C)/(2*(1-Floor)*AddOn))
	return min(1,Floor + (1-Floor)*multiplier)

def get_EAD(alpha,RC, multiplier,AddOn):
	return alpha * (RC + multiplier * AddOn)