import requests
import json
import re
import matplotlib.pyplot as plt
from datetime import datetime
import collections
import bisect
import numpy as np
from scipy import stats

##from stocktwits
def stockTwitsInfoRequest(symbolList):
    resultDictionary = {}
    for symbol in symbolList:
        r = ""
        print "looking for https://api.stocktwits.com/api/2/streams/symbol/"+symbol+".json"
        r = requests.post("https://api.stocktwits.com/api/2/streams/symbol/"+symbol+".json")
        print(r.status_code, r.reason)
        #print(r.content)
        resultDictionary[symbol] = r.content
    return resultDictionary

def stockQuoteRequest(symbol):
    stockQuoteDictionary = {}

    r = ""
    print "looking for http://chartapi.finance.yahoo.com/instrument/1.0/" + symbol + "/chartdata;type=quote;range=1d/json"
    r = requests.post("http://chartapi.finance.yahoo.com/instrument/1.0/" + symbol + "/chartdata;type=quote;range=1d/json")
    print(r.status_code, r.reason)
    #print(r.content)
    modified = r.content.split('series" : ', 1)[1]
    modified2 = modified.split('} )',1)[0]
    stockQuoteDictionary[symbol] = modified2
    return stockQuoteDictionary





#def stockTerms():
    #stockTermDictionary["BUY"]= "buy"


def main():
    #dictionary is a one time operation to be put in memory
    dictScore = loadSentimentDictionary("./dict/SentiWordNet_3.0.0_20130122.txt")
    #symbolList = ["MSFT"]
    symbolList = scrapDWJI30Symbols()
    resultsDict = stockTwitsInfoRequest(symbolList[:4])
    #print resultsDict
    timeScoreList = []
    for symbol in symbolList[:4]:
        listNews = parseJSON(resultsDict[symbol])
        for newsItem in listNews:
            #print newsItem.news
            #print newsItem.timestamp
            #print "score: " + str(scoreNews(newsItem.news, dictScore))
            timedScore = ComputedScoreTimed(scoreNews(newsItem.news, dictScore), newsItem.timestamp)
            timeScoreList.append(timedScore)
        #plotTimeSeriesNewsScore(timeScoreList,symbol)
        stockPriceDict = stockQuoteRequest(symbol)
        #for symbol in symbolList:
        timePriceList = parseJSONStockPrice(stockPriceDict[symbol])
        #plotTimeSeriesPrice(timePriceList,symbol)
        timeSeriesNewsScoreDict = getTimeSeriesNewsScore(timeScoreList)
        timeSeriesPrice = getTimeSeriesPrice(timePriceList)
        syncronizedPriceScoreDict = synchronizeNewsScorePrice(timeSeriesNewsScoreDict,timeSeriesPrice)
        plotPriceNewsScorePlot(syncronizedPriceScoreDict,symbol)
        #computeCorrelation(syncronizedPriceScoreDict)
        orderedScoreListByTime = sorted(timeScoreList, key=lambda x: x.timestamp, reverse=False)
        firstNewsTime = orderedScoreListByTime[0].timestamp
        lastNewsTime = orderedScoreListByTime[-1].timestamp
        printCorrelationResult(syncronizedPriceScoreDict,firstNewsTime,lastNewsTime,symbol)


class StockNews:

   def __init__(self, news, timestamp):
      self.news = news
      self.timestamp = timestamp


class TermScore:

   def __init__(self, avgScore, numberOfMeanings):
       self.avgScore = avgScore
       self.numberOfMeanings = numberOfMeanings

class ComputedScoreTimed:
    def __init__(self, score, timestamp):
        self.score = score
        self.timestamp = timestamp


class StockPrice:
    def __init__(self, price, timestamp):
        self.price = price
        self.timestamp = timestamp



def parseJSON(jsonContent):
    parsed_json = json.loads(jsonContent)
    test = json._default_decoder.decode(jsonContent)

    messages =  parsed_json["messages"]
    listStockNews=[]

    for message in messages:
        stockNews = StockNews(message["body"], message["created_at"])
        listStockNews.append(stockNews)
    return listStockNews

def parseJSONStockPrice(jsonContent):
    parsed_json = json.loads(jsonContent)
    test = json._default_decoder.decode(jsonContent)

    series = map(lambda x: StockPrice(x["close"], x["Timestamp"]), parsed_json) #parsed_json["Timestamp"]

    return series

    # Message = namedtuple("Message", "body, created_at")
    #
    # try:
    #     messages = [Message(**k) for k in parsed_json["messages"]]
    # except TypeError as e:
    #     print e
    # print messages
    #print json.dumps(parsed_json,indent=4)



def loadSentimentDictionary(filename):
    sentimentDictionary={}
    with open(filename) as f:
        for line in f:
            if(line.startswith("#")==False):
                data = line.split("\t")
                synsetScore = float(data[2]) - float(data[3])
                dataModified = re.sub('#.', "", data[4])
                synTermsSplit = dataModified.split(" ");
                for term in synTermsSplit:
                    if term in sentimentDictionary:
                        currentTerm = sentimentDictionary[term]
                        currentTerm.avgScore = (currentTerm.avgScore*currentTerm.numberOfMeanings+synsetScore)/(currentTerm.numberOfMeanings+1)
                        currentTerm.numberOfMeanings += 1
                        sentimentDictionary[term] = currentTerm
                    else:
                        currentTerm = TermScore(synsetScore,1)
                        sentimentDictionary[term] = currentTerm
    return sentimentDictionary



def scoreNews(news,corpusScore):
    termsInNews = news.split(" ")
    overallScore = 0
    for term in termsInNews:
        if term in corpusScore:
            termValue = corpusScore[term]
            score = termValue.avgScore
            overallScore += score
    return overallScore



def plotTimeSeriesNewsScore(timeSeriesScore,symbol):
    timeSeriesScore.sort(key=lambda x: x.timestamp, reverse=False)

    plt.ion()
    # x = np.array([datetime.datetime(2013, 9, 28, i, 0) for i in range(24)])
    # y = np.random.randint(100, size=x.shape)
    #
    x = map(lambda x: x.timestamp, timeSeriesScore)
    xx = map(lambda x: datetime.strptime(str(x), "%Y-%m-%dT%H:%M:%SZ"),x)
    #date_object = datetime.strptime(xx, '%Y-%m-%dT%HH:%MM:SS')
    y = map(lambda x: x.score, timeSeriesScore)
    fig = plt.figure()
    fig.suptitle('Stock Sentiment: ' + symbol, fontsize=14, fontweight='bold')
    plt.plot(xx, y)
    plt.xlabel("Date and Time")
    plt.ylabel("Sentiment Score (SentiWordNet scale)")
    #plt.ion()
    plt.draw()
    fig.savefig(symbol+"ScoreTS.png")
    #plt.show()


def getTimeSeriesNewsScore(timeSeriesScore):
    timeSeriesScore.sort(key=lambda x: x.timestamp, reverse=False)
    x = map(lambda x: x.timestamp, timeSeriesScore)
    xx = map(lambda x: datetime.strptime(str(x), "%Y-%m-%dT%H:%M:%SZ"), x)
    # date_object = datetime.strptime(xx, '%Y-%m-%dT%HH:%MM:SS')
    y = map(lambda x: x.score, timeSeriesScore)
    dictionary = dict(zip(xx, y))
    #print "dictionary done"
    return dictionary

def plotTimeSeriesPrice(timeSeriesPrice,symbol):
    plt.ion()
    #x = map(lambda x:datetime.fromtimestamp((item[0] for item in x.keys())).strftime('%Y-%m-%d %H:%M:%S'),timeSeriesPrice)
    x = map(lambda x: datetime.fromtimestamp(x.timestamp),timeSeriesPrice)
    y = map(lambda x: x.price,timeSeriesPrice)
    fig = plt.figure()
    fig.suptitle('Stock Price: '+symbol, fontsize=14, fontweight='bold')
    plt.plot(x, y)
    plt.xlabel("Time (CET timezone)")
    plt.ylabel("Price (USD)")
    #
    plt.draw()
    fig.savefig(symbol + "PriceTS.png")
    #plt.show()


def getTimeSeriesPrice(timeSeriesPrice):
    x = map(lambda x: datetime.fromtimestamp(x.timestamp), timeSeriesPrice)
    y = map(lambda x: x.price, timeSeriesPrice)
    dictionary = dict(zip(x, y))
    #print "dictionary done"
    return dictionary

def synchronizeNewsScorePrice(newsScoreDict,priceDict):
    plt.ion()
    timestampsNews = newsScoreDict.keys()
    od = collections.OrderedDict(sorted(priceDict.items()))
    synchPriceNewsDict = {}
    # x = []
    # y = []
    for timestamp in timestampsNews:


        # a = collections.OrderedDict()
        # for i in range(100):
        #     a[i] = i


        ind = bisect.bisect_left(od.keys(), timestamp)
        #quick and dirty way to handle boundary conditions
        if ind == 0:
            ind = 1
        elif ind == len(od.keys()):
            ind = len(od.keys()) - 1
            #################################
        #print timestamp
        #print od.keys()[ind-1]
        #print od.keys()[ind]
        if (timestamp - od.keys()[ind-1] > od.keys()[ind] - timestamp):
            synchPrice = priceDict[od.keys()[ind]]
        else:
            synchPrice = priceDict[od.keys()[ind-1]]

        synchPriceNewsDict[timestamp] = [synchPrice,newsScoreDict[timestamp]]
    # print "pippo"
    # for item in synchPriceNewsDict:
    #     x.append(synchPriceNewsDict[item][0])
    #     y.append(synchPriceNewsDict[item][1])

    # fig = plt.figure()
    # fig.suptitle('Price vs. News Sentiment Score: '+symbol, fontsize=14, fontweight='bold')
    # plt.xlabel("Price (USD)")
    # plt.ylabel("Sentiment Score (SentiWordNet scale)")
    # plt.scatter(x, y)
    # plt.draw()

    return synchPriceNewsDict



def plotPriceNewsScorePlot(synchPriceNewsDict, symbol):
    x = []
    y = []
    for item in synchPriceNewsDict:
        x.append(synchPriceNewsDict[item][0])
        y.append(synchPriceNewsDict[item][1])
    fig = plt.figure()
    fig.suptitle('Price vs. News Sentiment Score: ' + symbol, fontsize=14, fontweight='bold')
    plt.xlabel("Price (USD)")
    plt.ylabel("Sentiment Score (SentiWordNet scale)")
    plt.scatter(x, y)
    params = computeCorrelation(synchPriceNewsDict)
    y2 = map(lambda x2:params[0]*x2+params[1],x)
    plt.plot(x,y2, label="Linear Regression fit")
    plt.legend()

    fig.savefig(symbol + "PriceNews.png")

    plt.draw()

def printCorrelationResult(synchPriceNewsDict,firstNewsTime,lastNewsTime,symbol):
    params = computeCorrelation(synchPriceNewsDict)
    print "Correlation coefficient news sentiment and price for stock: " + symbol + " r=" + str(params[2])+ " during time interval "+firstNewsTime + " -- " + lastNewsTime



def computeCorrelation(synchPriceNewsDict):
    x = []
    y = []
    for item in synchPriceNewsDict:
        x.append(synchPriceNewsDict[item][0])
        y.append(synchPriceNewsDict[item][1])
    #print np.corrcoef(x, y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    return [slope, intercept, r_value, p_value, std_err]


def scrapDWJI30Symbols():
    print "looking for http://money.cnn.com/data/dow30/"
    print "retriving DWJI30 stocks symbols"
    r = requests.post("http://money.cnn.com/data/dow30/")
    print "response:",
    print(r.status_code, r.reason)
    #print r.content

    s = 'asdf=5;iwantthis123jasd'
    dwji30SymbolList = re.findall("class=\"wsod_symbol\">(.*)</a>", r.content)
    # for symbol in result:
    #     print symbol
    return dwji30SymbolList




#Execution main program
main()
raw_input("Press enter when done...")