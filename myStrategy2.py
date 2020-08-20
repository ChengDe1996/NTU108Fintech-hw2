import numpy as np
import pandas as pd
import sys
import argparse
'''
我主要使用的技術指標有 MA, EMA, MA based黃金交叉死亡交叉, RSI等等
最主要的策略是 因為我覺得拿來分析的股市資料長達10年 是非常長的
如果這10年間我們都只使用同一個策略或是同一組參數，明顯是不合理的，畢竟股市瞬息萬變，又何況是10年過去
所以我先嘗試了將資料隨時間切分成數個等分，在每段時間中，應用不同的技術指標當作主策略，但後來發現可能其實最基礎的MA就可以透過這樣的
方式表現得很好，所以最後便將策略改為 在數個時間區間中去finetune參數。
此外，我有將四隻股票的股價隨時間做圖，發現ＬＱＤ這之股票本身的獲利就特別低，所以我有在他身上花了很多的時間，嘗試各種不同的技術指標組合
最後採用了 以 EMA作為主技術指標，下去finetune後加上RSI一同判斷並去finetune RSI的參數，最後加上MA based的黃金交叉死亡交叉指標
重複以上步驟，最後相比於vanilla的MA，可以明顯提升performance。
最後總結，我覺得本次作業最大的重點就是，在長達10年的股市中，都使用同一種策略或是參數來買賣股票是不make sense的，在意識到這件事情
並進行改善後，整體的效果才有了大幅的提升

'''

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
    section = 1
    sec_len = 500
    for i in range(8):
        if (len(pastData)> i*sec_len):
            section = i+1
            continue
    MA_paramSetting={'SPY': {'alpha': [0, 0, 8, 4, 0, 0, 0, 0, 0], 'beta':[0, 2, 0, 5, 2, 6, 8, 4, 1], 'windowSize':[0, 3, 3, 4, 16, 3, 3, 8, 17]},
                    'IAU': {'alpha': [0, 0, 0, 0, 1, 0, 0, 0, 0], 'beta':[0, 1, 1, 2, 2, 0, 0, 1, 1], 'windowSize':[0, 3, 3, 3, 3, 8, 8, 3, 3]},
                    'LQD': {'alpha': [0, 0, 2, 0, 0, 1, 0, 0, 0], 'beta':[0, 1, 1, 1, 2, 2, 2, 1, 1], 'windowSize':[0, 3, 7, 26, 12, 3, 22, 30, 4]},
                    'DSI': {'alpha': [0, 3, 0, 0, 0, 2 ,0, 0, 0], 'beta':[0, 0, 1, 3, 4, 0, 2, 0, 0], 'windowSize':[0, 3, 7, 16, 29, 13, 8, 19, 0]}}
    LQD_paramSetting = {'LQD':{'w1':[0, 212, 256, 436, 200, 200, 297, 226, 432],'w2':[0, 211, 255, 435, 150, 157, 284, 217, 426]}}
    windowSize=MA_paramSetting[stockType]['windowSize'][section]
    alpha=MA_paramSetting[stockType]['alpha'][section]
    beta=MA_paramSetting[stockType]['beta'][section]
    if(stockType == 'LQD'):
        w1 = LQD_paramSetting[stockType]['w1'][section]
        w2 = LQD_paramSetting[stockType]['w2'][section]
    
    if stockType == 'LQD':
        action = EMA(pastData,currentPrice,w1,w2)
        action += RSI(pastData,currentPrice,47,38,62)   
        action += CrossOver(pastData,currentPrice,29,36)
        #action = MA(pastData, currentPrice, windowSize, alpha, beta)
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
    action=0      
    dataLen=len(pastData)
    if dataLen==0:
        return action
    # Compute ma
    if dataLen<windowSize:
        ma=np.mean(pastData)    
    else:
        windowedData=pastData[-windowSize:]    
        ma=np.mean(windowedData)
    # Determine action

    if (currentPrice-ma)>alpha: 
        action=1
    elif (currentPrice-ma)<-beta: 
        action=-1
    return action
def ema(windowSize):
    alpha = 2/(windowSize+1)
    weights = (1-alpha)**np.arange(windowSize)
    weights /= weights.sum()
    return weights[::-1]

def EMA(pastData,currentPrice,w1,w2):

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

    for windowSize in range(windowSizeMin, windowSizeMax+1):      
        print("windowSize=%d" %(windowSize))
        for alpha in range(alphaMin, alphaMax+1):   
            print("\talpha=%d" %(alpha))
            for beta in range(betaMin, betaMax+1):    
                print("\t\tbeta=%d" %(beta), end="")   
                returnRate=computeReturnRate(adjClose, windowSize, alpha, beta) 
                print(" ==> returnRate=%f " %(returnRate))
                if returnRate > returnRateBest:    
                    windowSizeBest=windowSize
                    alphaBest=alpha
                    betaBest=beta
                    returnRateBest=returnRate
    print("Best settings: windowSize=%d, alpha=%d, beta=%d ==> returnRate=%f" %(windowSizeBest,alphaBest,betaBest,returnRateBest))



