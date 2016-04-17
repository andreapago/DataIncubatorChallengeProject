# Data Incubator Challenge Project - Andrea Pagani
Sentiment analysis of messages of (financial) social media to predict stock price variations.



##Description:

###The idea:
The idea for my data incubator project can be summarized as predict or understand the movements in the price of stocks based on the opinion of people about those stocks. There is a lot information and people talking around stocks on the Internet such as Twitter, Facebook, News Feeds and specialized financial microblogging and forums such as Seeking Alpha and StockTwits.
The idea is to get data from all these sources and understand the minute-by-minute sentiment of the crowd about the stock of interest by looking at the terms and words used in the messages and the news about those stocks. At the same time, I monitor the price of the stock to discover, if at all, any form of correlation between the price of the stock and the sentiment of the crowd or influence of the sentiment on the price of the stock.

###The goal:
The dream is to make a system that can use the wisdom of the crowd to predict the changes in the stock price so we can make some bets on the stock market (and gain some money)!

###Technical description and details of the implemented code so far:
1)Web scraping (http://money.cnn.com/data/dow30/) to get the list of the components of the Dow Jones Industrial index to have the symbols of the stocks of interest.  
2)Messages concerning the stock of interest are retrieved by the financial microblogging stocktwits (http://http://stocktwits.com) by using the provided interface service i.e., REST API (http://stocktwits.com/developers).   
3)For each message retrieved concerning the stock of interest the content is analyzed word-by-word. In order to find the sentiment of each word I use a dictionary with words (i.e., SentiWordNet) and a sentiment score. SentiWordNet that is a lexical resource for opinion mining. SentiWordNet assigns to each word of the WordNet dictionary (http://wordnet.princeton.edu/) three sentiment scores: positivity, negativity, objectivity. Details of SentiWordNet can be found at http://sentiwordnet.isti.cnr.it/. At the moment the scores of each word (i.e., term) of each message are summed up (since single words have positive and negative values defining the sentiment) to get a single score for the whole message.     
4)For the stock of interest the minute-by-minute price is retrieved by scraping the yahoo financial services(http://chartapi.finance.yahoo.com/instrument/1.0/STOCKSYMBOL/chartdata;type=quote;range=1d/json).   
5)The news scores time series is synchronized with the price time series in order to have the pairs of news score and stock price. If news are issued in a timestamp where there is no trading, the synchronization is done to the closest timestamp when a stock price is available.  
6)Correlation between stock price and news score is performed.    
7)Plots are drawn of time series news score, time series stock price (minute-by-minute transactions), scatter plot news score vs. stock price with linear regression fit.

###Current Limitations and Future Works:
The following limitations are known and the goal is to address them during the 8-week program at Data Incubator.  
1)Stocktwits provides free of charge maximum 30 messages concerning a stock of interest. Possible solution: have a paid agreement with stocktwits (available in stocktwits premium services) for more messages.  
2)News and messages source is stocktwits. Possible solution: include other sources Seeking Alpha, Twitter, Facebook are likely candidates.  
3)Stock price feed of Yahoo is not for every transaction taking place on the market (but more likely a minute value). Possible solution: there are paid subscription services available with real-time services (also mentioned in the Data Incubator page is Quandl that offers this subscription).  
4)SentiWordNet should be extended with terms typical of financial word to stress their meaning. Possible solution: create ad-hoc dictionary with help of financial market experts.  
5)Synchronization of messages during non trading time. Possible solution: make a special score for that non-trading periods.  
6)Use some more sophisticated indicator than simple correlation coefficient. Possible solution: investigate non linear relationships and threshold effects. Test the fitting of non-linear models to the data. In addition, consider the integration of stochastic models in the prediction of variation.  
7)Use of Dow Jones Industrial 30 stock symbols. Possible solution: easily expandable to more markets.  
8)No distinction of user posting news or messages. Possible solution: provide ranking of users based on their posts and their influence of the price of the stock.  
9)The effect of delay (or anticipation) in the response of the market to the sentiment are not taken into account. Possible solution: consider a lag-based approach in computing correlations between the sentiment and the stock price.  
10)The analysis of volume exchange is not considered. Possible solution: investigate the relationship of the sentiment with the volume of shares exchanged as an additional element to take into account. 

###The scientific background:
There are scientific publications investigating this sort of approach of extracting the mood of messages to predict the stock market. Some non-exhaustive references are:  
Chen, H., De, P., Hu, Y. J., & Hwang, B. H. (2014). Wisdom of crowds: The value of stock opinions transmitted through social media. Review of Financial Studies, 27(5), 1367-1403.  
Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2013). Which news moves stock prices? a textual analysis (No. w18725). National Bureau of Economic Research.  
Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. Journal of Computational Science, 2(1), 1-8.  
