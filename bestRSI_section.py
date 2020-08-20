import sys
import numpy as np
import pandas as pd


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

# Decision of the current day by the current price, with 3 modifiable parameters
def myStrategy(pastData, currentPrice, windowSize, low, up):
    action = 0
    section = 1
    sec_len = 500
    stockType = 'LQD'
    for i in range(8):
        if (len(pastData)> i*sec_len):
            section = i+1
            continue
    LQD_paramSetting = {'LQD':{'w1':[0, 212, 256, 436, 200, 200, 297, 226, 432],'w2':[0, 211, 255, 435, 150, 157, 284, 217, 426]}}
    w1 = LQD_paramSetting[stockType]['w1'][section]
    w2 = LQD_paramSetting[stockType]['w2'][section]
    action = EMA(pastData,currentPrice,w1,w2)
    action += RSI(pastData, currentPrice, windowSize, low, up)
    
    real_action = 0

    if action>0:
        real_action = 1
    elif action == 0:
        real_action = 0
    else:
        real_action = -1

    return real_action







# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, windowSize, low, up, section):
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
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, windowSize, low, up)		# Obtain the suggested action
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
	returnRateBest=-1.00	 # Initial best return rate
	df=pd.read_csv(sys.argv[1])	# read stock file
	adjClose=df["Adj Close"].values		# get adj close as the price vector
	windowMin=5; windowMax=40;	# Range f windowSize to explore
	lowMin=1;	lowMax = 40
	upMin = 60; upMax = 99			# Range of alpha to explore
	windowSizeBest = [0,0,0,0,0,0,0,0,0]
	lowBest = [0,0,0,0,0,0,0,0,0]
	upBest = [0,0,0,0,0,0,0,0,0]
	for i in range(1,9):
		for windowSize in range(windowMin, windowMax+1):		# For-loop for windowSize
			print("windowSize=%d" %(windowSize))
			for low in range(lowMin, lowMax+1):	    	# For-loop for alpha
				print("\tlow=%d" %(low))
				for up in range(upMin,upMax+1):
					print("\tup=%d" %(up))

					returnRate=computeReturnRate(adjClose, windowSize, low, up, i)		# Start the whole run with the given parameters
					print(" ==> returnRate=%f " %(returnRate))
					if returnRate > returnRateBest:		# Keep the best parameters
						windowSizeBest[i] = windowSize
						lowBest[i] = low
						upBest[i] = up
						returnRateBest=returnRate
	print(args.input)
	print('windowSizeBest: ',windowSizeBest)
	print('lowBest: ', alphaBest)
	print('upBest: ', betaBest)