from textblob_nl import PatternTagger, PatternAnalyzer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline


def textblob(text):
    return TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())


def pos_or_neg_textblob(score):
    if score[0] < 0:
        return 'negative'
    else:
        return 'positive'


analyzer = SentimentIntensityAnalyzer()


def vader(text):
    return analyzer.polarity_scores(text)


def pos_or_neg_vader(score):
    if score.get('compound') < 0:
        return 'negative'
    else:
        return 'positive'


tokenizer = AutoTokenizer.from_pretrained("DTAI-KULeuven/robbert-v2-dutch-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("DTAI-KULeuven/robbert-v2-dutch-sentiment")
classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)


def transformer(text):
    return classifier(text)


def pos_or_neg_transformer(score):
    return score[0].get('label')


def get_sentiment(data, analysis_type='Textblob'):
    """
    Get sentiment of data with data being an array of answers and analysis type (Textblob/Vader/Transformer)
    """
    results = []
    if analysis_type == 'Textblob':
        for answer in data:
            if answer != '':
                results.append(pos_or_neg_textblob(textblob(answer).sentiment))
            else:
                results.append('')
    elif analysis_type == 'Vader':
        for answer in data:
            if answer != '':
                results.append(pos_or_neg_vader(vader(answer)))
            else:
                results.append('')
    elif analysis_type == 'Transformer':
        for answer in data:
            if answer != '':
                results.append(pos_or_neg_transformer(transformer(answer)))
            else:
                results.append('')
    else:
        return 'Verkeerde analyse.'
    return results


def get_sentiment_of_dataset(dataset, columns, exclude=True, analysis_type="Textblob"):
    data_with_columns = dataset.drop(columns, axis=1) if exclude else dataset[columns]

    total_sentiment = {}

    for label, series in data_with_columns.items():
        result = get_sentiment(series, analysis_type)
        total_sentiment[label] = {'positive': sum([1 for s in result if 'positive' in s]), 'negative': sum([1 for s in result if 'negative' in s])}

    return total_sentiment
