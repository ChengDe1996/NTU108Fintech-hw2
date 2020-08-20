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

def myStrategy(pastData, currentPrice, windowSize, section, alpha, beta):
	action = 0

	action = MA(pastData, currentPrice, windowSize, alpha, beta)
	if action>0:
		real_action = 1
	elif action == 0:
		real_action = 0
	else:
		real_action = -1

	return real_action





# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, windowSize, alpha, beta, section):
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
		'''
		if(section == 1 and ic > 1000):
			break
	
		if(section == 2 and len(dataCount) <= 1000):
			continue
		if(section == 2 and len(dataCount) > 2000):
			break
		if(section == 3 and len(dataCount) <= 2000):
			continue
		if(section == 3 and len(dataCount) > 3000 ):
			break
		if(section == 4 and len(da))
		'''
		currentPrice=priceVec[ic]	# current price
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, windowSize, section, alpha, beta)
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
    windowSizeMin = 3; windowSizeMax=30;	# Range f windowSize to explore
    alphaMin=0;	alphaMax = 10
    betaMin = 0; betaMax = 20			# Range of alpha to explore
    windowSizeBest = [0,0,0,0,0,0,0,0,0]
    alphaBest = [0,0,0,0,0,0,0,0,0]
    betaBest = [0,0,0,0,0,0,0,0,0]
    #section = args.section
    for i in range(1,9):
    	returnRateBest = -1.00
    	for windowSize in range(windowSizeMin, windowSizeMax+1):
    		print("windowSize=%d" %(windowSize))
    		for alpha in range(alphaMin, alphaMax+1):
    			print("\talpha=%d" %(alpha))
    			for beta in range(betaMin, betaMax+1):
    				print("\t\tbeta=%d" %(beta), end="")
    				returnRate=computeReturnRate(adjClose, windowSize, alpha, beta, i)
    				print(" ==> returnRate=%f " %(returnRate))
    				if returnRate > returnRateBest:	
    					windowSizeBest[i] = windowSize
    					alphaBest[i] = alpha
    					betaBest[i] = beta
    					returnRateBest=returnRate
    #print("Best settings: windowSize=%d, alpha=%d, beta=%d ==> returnRate=%f" %(windowSizeBest,alphaBest,betaBest,returnRateBest))
    print(args.input)
    print('windowSizeBest: ',windowSizeBest)
    print('alphaBest: ', alphaBest)
    print('betaBest: ', betaBest)

