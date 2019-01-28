import pytest
import pandas as pd
import numpy as np
from helper import *

def test_maturity_factor():
	start_date = ["2018-01-10T00:00:00Z","2019-01-10T00:00:00Z"]
	end_date = ["2018-04-10T00:00:00Z","2021-01-10T00:00:00Z"]
	trade_date = ["2018-01-10T00:00:00Z","2019-01-10T00:00:00Z"] 

	assert maturity_factor(pd.to_datetime(start_date[1]),pd.to_datetime(end_date[1]),pd.to_datetime(trade_date[1])) == 1

def test_supervisory_duration():
	assert abs(supervisory_duration(0,10)-7.86938680574733)<=0.1
	assert abs(supervisory_duration(0,4)-3.62538493844036)<=0.1

def test_option_delta():
	assert abs(option_delta(False,False,0.06,0.05,0.5,1)-(0.269395217710533))<=0.1

def test_effective_notional():
	assert abs(round(effective_notional(0,-36254,78694)) - 59270)<=0.1
	assert abs(effective_notional(0,0,-10083) - 10083)<=0.1

def test_get_multiplier():
	assert abs(get_multiplier(0.005,100,60,629)-1)<=0.1
	assert abs(get_multiplier(0.005,80,100,437)-0.97726) <=0.01

def test_get_EAD():
	assert abs(round(get_EAD(1.4,0,0.958,1401))-1879)<=1
	assert abs(round(get_EAD(1.4,40,1,629))-936)<=1