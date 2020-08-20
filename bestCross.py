import sys
import numpy as np
import pandas as pd
from talib import abstract

def SMA(pastData,currentPrice,windowSize):
    SMAu = 0
    SMAd = 0
    temp = pastData[-windowSize:]
    for i in range(windowSize-1):
        if temp[i]<temp[i+1]:
            SMAu += temp[i+1]-temp[i]
        else:
            SMAd += temp[i]-temp[i+1]
    return SMAu/windowSize,SMAd/windowSize
# Decision of the current day by the current price, with 3 modifiable parameters

def KD(pastData,currentPrice):
	pastData = pd.DataFrame(pastData)
	K,D = abstract.STOCH(pastData)
	return K,D


def myStrategy(pastData, currentPrice, s, l):
	action = 0
	if(len(pastData)<l):
		return action
	action = 0
	action = EMA(pastData,currentPrice,317,222)
	action += RSI(pastData,currentPrice,47,38,62)
	action += CrossOver(pastData,currentPrice,s,l)
	if action>0:
		real_action = 1
	elif action == 0:
		real_action = 0
	else:
		real_action = -1

	return real_action


def RSI(pastData,currentPrice,windowSize,low,up):
    action = 0
    if(len(pastData)<5):
        action = 0
        return action
    if(len(pastData)<windowSize):
        windowSize = len(pastData)
    SMAu,SMAd = SMA(pastData, currentPrice, windowSize)
    value = SMAu/(SMAu+SMAd)
    if(int(value*100)>up):
        action = -1
    if(int(value*100)<low):
        action = 1
    return action


def ema(windowSize):
    alpha = 2/(windowSize+1)
    weights = (1-alpha)**np.arange(windowSize)
    weights /= weights.sum()
    return weights[::-1]

def EMA(pastData,currentPrice,w1,w2):#windowSize = [546, 90]

    dataLen = len(pastData)
    if dataLen < w1+2:
        return 0

    L_weights = ema(w1)
    M_weights = ema(w2)
    L_ma = np.dot(L_weights, np.append(pastData[-w1+1:], [currentPrice]))
    L_ma_past = np.dot(L_weights, pastData[-w1-1:-1])
    M_ma = np.dot(M_weights, np.append(pastData[-w2+1:], [currentPrice]))
    M_ma_past = np.dot(M_weights, pastData[-w2-1:-1])

    if(M_ma > L_ma and M_ma_past < L_ma_past):
        action=1
    elif(M_ma < L_ma  and M_ma_past > L_ma_past):
        action=-1
    else:
        action=1

    return action


def CrossOver(pastData,currentPrice,s,l):
    action = 0
    shortpast = np.mean(pastData[-s:])
    longpast = np.mean(pastData[-l:])
    pastData = list(pastData)
    pastData.append(currentPrice)
    pastData = np.array(pastData)
    shortcur = np.mean(pastData[-s:])
    longcur = np.mean(pastData[-l:])
    if(shortpast<longpast and shortcur>longcur):
        action = 1
    elif (longpast < shortpast and longcur > shortcur):
        action = -1
    else:
        action = 0

    return action
# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, s,l):
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
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, s,l)		# Obtain the suggested action
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
	sMin=3; sMax=20;	# Range f windowSize to explore
	lMin=15;	lMax = 60
	upMin = 60; upMax = 99			# Range of alpha to explore
	#betaMin=13; betaMax=18				# Range of beta to explore
	# Start exhaustive search
	sBest=0
	lBest = 0
	upBest = 0
	for s in range(sMin, sMax+1):		# For-loop for windowSize
		print("s=%d" %(s))
		for l in range(lMin, lMax+1,5):	    	# For-loop for alpha
			print("\tl=%d" %(l))
			returnRate=computeReturnRate(adjClose, s, l)		# Start the whole run with the given parameters
			print(" ==> returnRate=%f " %(returnRate))
			if returnRate > returnRateBest:		# Keep the best parameters
				sBest = s
				lBest = l
				#upBest = up
				returnRateBest=returnRate
	print("Best settings: s=%d, l=%d ==> returnRate=%f" %(sBest,lBest,returnRateBest))		# Print the best result
