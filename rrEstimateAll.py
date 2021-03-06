# How to invoke this program:
#	python rrEstimateAll.py
import sys
import numpy as np
import pandas as pd
from myStrategy2 import myStrategy
import matplotlib.pyplot as plt

# Compute return rate over a given price vector
def computeReturnRate(priceVec, stockType):
	capital=1000	# Initial available capital
	capitalOrig=capital	 # original capital
	dataCount=len(priceVec)				# day size
	suggestedAction=np.zeros((dataCount,1))	# Vec of suggested actions
	stockHolding=np.zeros((dataCount,1))  	# Vec of stock holdings
	total=np.zeros((dataCount,1))	 	# Vec of total asset
	realAction=np.zeros((dataCount,1))	# Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
	# Run through each day
	temp = []
	for ic in range(dataCount):
		currentPrice=priceVec[ic]	# current price
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, stockType)		# Obtain the suggested action
		# get real action by suggested action
		if ic>0:
			stockHolding[ic]=stockHolding[ic-1]	# The stock holding from the previous day
		if suggestedAction[ic]==1:	# Suggested action is "buy"
			if stockHolding[ic]==0:		# "buy" only if you don't have stock holding
				stockHolding[ic]=capital/currentPrice # Buy stock using cash
				capital=0	# Cash
				realAction[ic]=1
		elif suggestedAction[ic]==-1:	# Suggested action is "sell"
			if stockHolding[ic]>0:		# "sell" only if you have stock holding
				capital=stockHolding[ic]*currentPrice # Sell stock to have cash
				stockHolding[ic]=0	# Stocking holding
				realAction[ic]=-1
		elif suggestedAction[ic]==0:	# No action
			realAction[ic]=0
		else:
			print(suggestedAction[ic])
			assert False
		total[ic]=capital+stockHolding[ic]*currentPrice	# Total asset, including stock holding and cash 
		temp.append(total[ic])
	returnRate=(total[-1]-capitalOrig)/capitalOrig		# Return rate of this run
	plt.plot(temp)
	plt.show()
	return returnRate
	
if __name__=='__main__':
	fileList=['SPY.csv', 'DSI.csv', 'IAU.csv', 'LQD.csv']
	fileCount=len(fileList);
	rr=np.zeros((fileCount,1))
	for ic in range(fileCount):
		file=fileList[ic];
		df=pd.read_csv(file)	
		adjClose=df["Adj Close"].values	# Get adj close as the price vector
		stockType=file[0:3]		# Get stock type
		rr[ic]=computeReturnRate(adjClose, stockType)	# Compute return rate
		print("file=%s ==> rr=%f" %(file, rr[ic]));
	print("Average return rate = %f" %(np.mean(rr)))