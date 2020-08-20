import sys
import numpy as np
import pandas as pd
import time
def ema(windowSize):
    alpha = 2/(windowSize+1)
    weights = (1-alpha)**np.arange(windowSize)
    weights /= weights.sum()
    return weights[::-1]
# Decision of the current day by the current price, with 3 modifiable parameters
def myStrategy(pastData, currentPrice, w1, w2):
    windowSize = [w1, w2]
    dataLen = len(pastData)
    if dataLen < max(windowSize)+2:
        return 0

    L_weights = ema(windowSize[0])
    M_weights = ema(windowSize[1])
    L_ma = np.dot(L_weights, np.append(pastData[-windowSize[0]+1:], [currentPrice]))
    L_ma_past = np.dot(L_weights, pastData[-windowSize[0]-1:-1])
    print(M_weights.shape, np.append(pastData[-windowSize[1]+1:], [currentPrice]))
    time.sleep(10)
    M_ma = np.dot(M_weights, np.append(pastData[-windowSize[1]+1:], [currentPrice]))
    M_ma_past = np.dot(M_weights, pastData[-windowSize[1]-1:-1])

    if(M_ma > L_ma and M_ma_past < L_ma_past):
        action=1
    elif(M_ma < L_ma  and M_ma_past > L_ma_past):
        action=-1
    else:
        action=1

    return action

# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, w1, w2):
	capital=1000	# Initial available capital
	capitalOrig=capital	 # original capital
	dataCount=len(priceVec)				# day size
	suggestedAction=np.zeros((dataCount,1))	# Vec of suggested actions
	stockHolding=np.zeros((dataCount,1))  	# Vec of stock holdings
	total=np.zeros((dataCount,1))	 	# Vec of total asset
	realAction=np.zeros((dataCount,1))	# Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
	# Run through each day
	for ic in range(dataCount):
		currentPrice=priceVec[ic]	# current price
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, w1, w2)		# Obtain the suggested action
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
			assert False
		total[ic]=capital+stockHolding[ic]*currentPrice	# Total asset, including stock holding and cash 
	returnRate=(total[-1]-capitalOrig)/capitalOrig		# Return rate of this run
	return returnRate

if __name__=='__main__':
	returnRateBest=-1.00	 # Initial best return rate
	df=pd.read_csv(sys.argv[1])	# read stock file
	adjClose=df["Adj Close"].values		# get adj close as the price vector
	w1Min=200; w1Max=500;	# Range f windowSize to explore
	w2Min=150;			# Range of alpha to explore
	#betaMin=13; betaMax=18				# Range of beta to explore
	# Start exhaustive search

	for w1 in range(w1Min, w1Max+1):		# For-loop for windowSize
		print("w1=%d" %(w1))
		for w2 in range(w2Min, w1+1):	    	# For-loop for alpha
			print("\tw2=%d" %(w2))
			returnRate=computeReturnRate(adjClose, w1, w2)		# Start the whole run with the given parameters
			print(" ==> returnRate=%f " %(returnRate))
			if returnRate > returnRateBest:		# Keep the best parameters
				w1Best=w1
				w2Best=w2
				returnRateBest=returnRate
	print("Best settings: w1=%d, w2=%d ==> returnRate=%f" %(w1Best,w2Best,returnRateBest))		# Print the best result

	returnRate = computeReturnRate(adjClose,317,222)
	print(returnRate)