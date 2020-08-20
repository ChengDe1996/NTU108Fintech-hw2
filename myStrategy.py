import numpy as np
import pandas as pd
import sys
import argparse

def parse_args():
    """ Parse args. """
    parser = argparse.ArgumentParser()
    # initial
    parser.add_argument('-m', '--ma', type = int, default = 3, help='Moving Average')
    parser.add_argument('-r', '--rsi', type = int, default = 10, help='Relative strength indicator')
    parser.add_argument('-i','--input', help = 'input file')
    args = parser.parse_args()
    return args
# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, windowSize, alpha, beta):
    capital=1000    # Initial available capital
    capitalOrig=capital  # original capital
    dataCount=len(priceVec)             # day size
    suggestedAction=np.zeros((dataCount,1)) # Vec of suggested actions
    stockHolding=np.zeros((dataCount,1))    # Vec of stock holdings
    total=np.zeros((dataCount,1))       # Vec of total asset
    realAction=np.zeros((dataCount,1))  # Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
    # Run through each day
    for ic in range(dataCount):
        currentPrice=priceVec[ic]   # current price
        suggestedAction[ic]=MA(priceVec[0:ic], currentPrice, windowSize, alpha, beta)       # Obtain the suggested action
        #suggestedAction[ic]=EMA(priceVec[0:ic], currentPrice, 546, 90)
        # get real action by suggested action
        if ic>0:
            stockHolding[ic]=stockHolding[ic-1] # The stock holding from the previous day
        if suggestedAction[ic]==1:  # Suggested action is "buy"
            if stockHolding[ic]==0:     # "buy" only if you don't have stock holding
                stockHolding[ic]=capital/currentPrice # Buy stock using cash
                capital=0   # Cash
                realAction[ic]=1
        elif suggestedAction[ic]==-1:   # Suggested action is "sell"
            if stockHolding[ic]>0:      # "sell" only if you have stock holding
                capital=stockHolding[ic]*currentPrice # Sell stock to have cash
                stockHolding[ic]=0  # Stocking holding
                realAction[ic]=-1
        elif suggestedAction[ic]==0:    # No action
            realAction[ic]=0
        else:
            assert False
        total[ic]=capital+stockHolding[ic]*currentPrice # Total asset, including stock holding and cash 
    returnRate=(total[-1]-capitalOrig)/capitalOrig      # Return rate of this run
    return returnRate




def myStrategy(pastData, currentPrice, stockType):
    action = 0
    #spy 6 23 12
    #iau 0 2 26
    #lqd 0 1 5
    #dsi 2 10 17
    section = 0
    if (len(pastData)<1000):
        section = 1
    elif (len(pastData)<2000):
        section = 2
    elif (len(pastData)<3000):
        section = 3
    else:
        section = 4

    '''
    MA_paramSetting={'SPY': {'alpha': {'1': 4,'2': 4, '3': 1, '4': 1}, \
                                'beta':{'1': 5,'2': 5, '3': 8, '4': 3}, \
                            'windowSize':{'1': 27,'2': 4, '3': 8, '4': 6}},
                    'IAU': {'alpha': {'1': 0,'2': 0, '3': 0, '4': 0}, \
                                'beta':{'1': 1,'2': 2, '3': 0, '4': 1}, \
                            'windowSize':{'1': 3,'2': 3, '3': 8, '4': 3}},
                    'LQD': {'alpha': {'1': 0,'2': 1, '3': 1, '4': 0}, \
                                'beta':{'1': 1,'2': 2, '3': 2, '4': 1}, \
                            'windowSize':{'1': 4,'2': 13, '3': 7, '4': 10}},
                    'DSI': {'alpha': {'1': 2,'2': 0, '3': 0, '4': 0}, \
                                'beta':{'1': 3,'2': 3, '3': 2, '4': 0}, \
                            'windowSize':{'1': 17,'2': 12, '3': 3, '4': 19}}}
    '''
    MA_paramSetting={'SPY': {'alpha': [0,4, 4, 1, 1], 'beta':[0, 5, 5, 8, 3], 'windowSize':[0, 27, 4, 8, 6]},
                    'IAU': {'alpha': [0, 0, 0, 0, 0], 'beta':[0, 1, 2, 0, 1], 'windowSize':[0, 3, 3, 8, 3]},
                    'LQD': {'alpha': [0, 0, 1, 1, 0], 'beta':[0, 1, 2, 2, 1], 'windowSize':[0, 4, 13, 7, 10]},
                    'DSI': {'alpha': [0, 2, 0, 0, 0], 'beta':[0, 3, 3, 2, 0], 'windowSize':[0, 17, 12, 3, 19]}}
    windowSize=MA_paramSetting[stockType]['windowSize'][section]
    alpha=MA_paramSetting[stockType]['alpha'][section]
    beta=MA_paramSetting[stockType]['beta'][section]
    
    if stockType == 'LQD':
        action = EMA(pastData,currentPrice,317,222)
        action += RSI(pastData,currentPrice,47,38,62)
        action += CrossOver(pastData,currentPrice,29,36)
    else:
        action = MA(pastData, currentPrice, windowSize, alpha, beta)
        #action += CrossOver(pastData,currentPrice,5,20)
        #action += RSI(pastData,currentPrice,14,10,90)

    real_action = 0
    

    #action = CrossOver(pastData, currentPrice, 5,20)
    if action>0:
        real_action = 1
    elif action == 0:
        real_action = 0
    else:
        real_action = -1

    # action = 0 or 1 or -1
    # ....
    # ....
    # ....
    # ....
    # ....
    return real_action

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





if __name__=='__main__':
    args = parse_args()
    returnRateBest=-1.00     # Initial best return rate
    df=pd.read_csv(args.input) # read stock file
    adjClose=df["Adj Close"].values     # get adj close as the price vector

    windowSizeMin=3; windowSizeMax=6;   # Range of windowSize to explore
    alphaMin=5; alphaMax=10;            # Range of alpha to explore
    betaMin=13; betaMax=18              # Range of beta to explore
    # Start exhaustive search

    for windowSize in range(windowSizeMin, windowSizeMax+1):        # For-loop for windowSize
        print("windowSize=%d" %(windowSize))
        for alpha in range(alphaMin, alphaMax+1):           # For-loop for alpha
            print("\talpha=%d" %(alpha))
            for beta in range(betaMin, betaMax+1):      # For-loop for beta
                print("\t\tbeta=%d" %(beta), end="")    # No newline
                returnRate=computeReturnRate(adjClose, windowSize, alpha, beta)     # Start the whole run with the given parameters
                print(" ==> returnRate=%f " %(returnRate))
                if returnRate > returnRateBest:     # Keep the best parameters
                    windowSizeBest=windowSize
                    alphaBest=alpha
                    betaBest=beta
                    returnRateBest=returnRate
    print("Best settings: windowSize=%d, alpha=%d, beta=%d ==> returnRate=%f" %(windowSizeBest,alphaBest,betaBest,returnRateBest))



