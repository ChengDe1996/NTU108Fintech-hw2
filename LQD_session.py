import sys
import numpy as np
import pandas as pd
import argparse
import time

# Decision of the current day by the current price, with 3 modifiable parameters

def parse_args():
    """ Parse args. """
    parser = argparse.ArgumentParser()
    # initial
    #parser.add_argument('-m', '--ma', type = int, default = 3, help='Moving Average')
    parser.add_argument('-s', '--section', type = int, default = 1, help='section number')
    parser.add_argument('-i','--input', help = 'input file')
    args = parser.parse_args()
    return args


def MA(pastData, currentPrice, windowSize, alpha, beta):
    action=0        # action=1(buy), -1(sell), 0(hold), with 0 as the default action
    dataLen=len(pastData)       # Length of the data vector
    if dataLen==0:
        return action
    # Compute ma
    if dataLen<windowSize:
        ma=np.mean(pastData)    # If given price vector is small than windowSize, compute MA by taking the average
    else:
        windowedData=pastData[-windowSize:]     # Compute the normal MA using windowSize
        ma=np.mean(windowedData)
    # Determine action

    if (currentPrice-ma)>alpha:     # If price-ma > alpha ==> buy
        action=1
    elif (currentPrice-ma)<-beta:   # If price-ma < -beta ==> sell
        action=-1
    return action

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
    #print(M_weights.shape, np.append(pastData[-windowSize[1]+1:], [currentPrice]))
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
def computeReturnRate(priceVec, w1, w2, section):
	capital=1000	# Initial available capital
	capitalOrig=capital	 # original capital
	dataCount=len(priceVec)				# day size
	suggestedAction=np.zeros((dataCount,1))	# Vec of suggested actions
	stockHolding=np.zeros((dataCount,1))  	# Vec of stock holdings
	total=np.zeros((dataCount,1))	 	# Vec of total asset
	realAction=np.zeros((dataCount,1))	# Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
	# Run through each day
	last = 0
	sec_len = 500
	for ic in range(dataCount):
		last = ic
		if( ic > section*sec_len):
			break
		if(ic <= (section-1)*sec_len and section != 1):
			continue

		currentPrice=priceVec[ic]	# current price
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, w1, w2)
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
	returnRate=(total[last-1]-capitalOrig)/capitalOrig		# Return rate of this run
	return returnRate

if __name__=='__main__':
    args = parse_args()
    returnRateBest=-1.00	 # Initial best return rate
    df=pd.read_csv(args.input)	# read stock file
    adjClose=df["Adj Close"].values		# get adj close as the price vector
    w1Min = 200; w1Max=500;	# Range f windowSize to explore
    w2Min= 150;
    #betaMin = 0; betaMax = 20			# Range of alpha to explore
    w1Best = [0,0,0,0,0,0,0,0,0]
    w2Best = [0,0,0,0,0,0,0,0,0]
    #betaBest = [0,0,0,0,0,0,0,0,0]
    #section = args.section
    for i in range(1,9):
    	returnRateBest = -1.00
    	for w1 in range(w1Min, w1Max+1):
    		print("w1=%d" %(w1))
    		for w2 in range(w2Min, w1):
    			print("\tw2=%d" %(w2))
    			returnRate=computeReturnRate(adjClose, w1, w2, i)
    			print(" ==> returnRate=%f " %(returnRate))
    			if returnRate > returnRateBest:	
    				w1Best[i] = w1
    				w2Best[i] = w2
    				#betaBest[i] = beta
    				returnRateBest=returnRate
    #print("Best settings: windowSize=%d, alpha=%d, beta=%d ==> returnRate=%f" %(windowSizeBest,alphaBest,betaBest,returnRateBest))
    print(args.input)
    print('w1: ',w1Best)
    print('w2: ', w2Best)
    #print('betaBest: ', betaBest)

