# Trigger Warning #
Ever accidentally offended someone or been unintentionally offended? Here's a self-updating NLP-based system to identify (and discourage) inflammatory content.

## Overview ##
![alt text](https://github.com/philhchen/trigger-warning/blob/master/imgs/Trigger%20Warning-2.png)
There are three components to this project:

The first is a **data processing pipeline** that downloads Tweets from the online database of Tweets, 
passes the Tweets through sentiment analysis software (Google and Microsoft APIs), 
and scores each Tweet based on the "consensus sentiment" among its replies and quotes.

The second is a **hybrid RNN/CNN-based model** that predicts how likely a post is to elicit a negative response. 
We use the data processing pipeline to train the model.

The third is a **Chrome extension** that uses the model created in the second component to recommend users to reconsider 
their comments or posts if the model detects a very inflammatory post.

## Why ##
The advantage of this model over current approaches is that it is both **dynamic** and **comprehensive**. 

Traditional flagging of comments or posts depends on static language models that detect certain trigger words, 
but our system provides the necessary pipeline to learn the latest issues.

Furthermore, current sentiment analysis models only consider sentences and paragraphs, 
but our pipeline is developed with the idea that the internet is an **interactive** space. 
Therefore, our program is specifically designed to reflect the sentiment raised in **responses** to comments and posts,
rather than the comments and posts themselves.

Finally, identifying potential "trigger words" is not enough because language, especially internet language, is far more **nuanced**,
which is reflected in our hybrid RNN/CNN model.
For example, **James Damore's letter**, which sparked intense backlash, was written with language that would have easily fooled 
more naive systems. The LSTM components of the model tend to convey an overall "context" to the final layers of the neural network,
whereas the CNN components tend to identify phrases that are strongly linked to controversy.

