# Calculator for sa-ccr
A Python implementation to calculate the counterparty credit risk under [Basel III Standardized Approach for Counterparty Credit Risk Management](https://www.bis.org/publ/bcbs279.htm)

## Conditions:
* IRS and Swaption only
* Unmargined trades only

## How-to Guide

1. Run the calculator in Powershell/Terminal

```shell
python calculator.py
Please enter name of the json file without ending:
# Enter "sample" to run through the examples in the exercise sheet
# You can also enter "example" to go through Example 1 in the reg text's appendix

# Result should be saved in an Excel file called "Output", under the "Result" tab
```

2. 
Run unittest in Powershell/Terminal
```shell
pytest
```