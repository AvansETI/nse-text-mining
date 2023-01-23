from nltk.corpus import webtext
import seaborn as sns
from nltk.corpus import stopwords
import nltk
from textblob import TextBlob
from textblob_nl import PatternTagger, PatternAnalyzer
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import BigramCollocationFinder
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use("dark_background")
nltk.download('webtext')

# biagram_collocation = BigramCollocationFinder.from_words(words)
# biagram_collocation.nbest(BigramAssocMeasures.raw_freq, 10)

# stopset = set(stopwords.words('dutch'))


# def filter_stops(w):
#     return len(w) < 3 or w in stopset


# biagram_collocation.apply_word_filter(filter_stops)
# biagram_collocation.nbest(BigramAssocMeasures.raw_freq, 10)


def positivity_rating(bigramlist):

    positiveList = {'goed': 1,
                    'tevreden': 1,
                    'fijn': 1,
                    'top': 1,
                    'fijne': 1,
                    'prettig': 1,
                    'duidelijk': 1,
                    'gezellig': 1}

    extrabonusList = {'erg': 1,
                      'heel': 1,
                      'zeer': 1}

    positiverating = 0
    rotation = 0

    for x in bigramlist['bigram']:
        cutlist = x.split()
        addedcounter = 0

        if cutlist[1] in positiveList:
            addedcounter += 1
            if cutlist[0] in extrabonusList:
                addedcounter += 1

        if addedcounter > 0:
            totalcount = addedcounter * bigramlist['frequency'][rotation]
            positiverating += totalcount

        rotation += 1

    return positiverating


def negativity_rating(bigramlist):

    negativeList = {'slecht': 1,
                    'ontevreden': 1,
                    'onprettig': 1,
                    'onfijn': 1,
                    'onduidelijk': 1,
                    'onfijne': 1,
                    'respectloos': 1,
                    'aggressief': 1,
                    'agressieve': 1,
                    'slechte': 1,
                    'ongezellig': 1}

    extrabonusList = {'erg': 1,
                      'heel': 1,
                      'zeer': 1}

    positiverating = 0
    rotation = 0

    for x in bigramlist['bigram']:
        cutlist = x.split()
        addedcounter = 0

        if cutlist[1] in negativeList:
            addedcounter += 1
            if cutlist[0] in extrabonusList:
                addedcounter += 1

        if addedcounter > 0:
            totalcount = addedcounter * bigramlist['frequency'][rotation]
            positiverating += totalcount

        rotation += 1

    return positiverating


def question_positivity_score(question):
    testlist = ['']

    stopset = set(stopwords.words('dutch'))
    c_vec = CountVectorizer(stop_words=stopset, ngram_range=(2, 3))

    testlist[0] = question
    posscore = 0
    try:
        ngrams_single = c_vec.fit_transform(testlist)
        count_values_single = ngrams_single.toarray().sum(axis=0)
        vocab_single = c_vec.vocabulary_
        df_ngram_single = pd.DataFrame(sorted([(count_values_single[i], k) for k, i in vocab_single.items()], reverse=True)
                                       ).rename(columns={0: 'frequency', 1: 'bigram'})

        posscore = positivity_rating(df_ngram_single)
    except:
        posscore = 0

    return posscore


def question_negative_score(question):
    testlist = ['']

    stopset = set(stopwords.words('dutch'))
    c_vec = CountVectorizer(stop_words=stopset, ngram_range=(2, 3))

    testlist[0] = question
    posscore = 0
    try:
        ngrams_single = c_vec.fit_transform(testlist)
        count_values_single = ngrams_single.toarray().sum(axis=0)
        vocab_single = c_vec.vocabulary_
        df_ngram_single = pd.DataFrame(sorted([(count_values_single[i], k) for k, i in vocab_single.items()], reverse=True)
                                       ).rename(columns={0: 'frequency', 1: 'bigram'})

        posscore = negativity_rating(df_ngram_single)
    except:
        posscore = 0

    return posscore


def question_search_miner(q, smallset, search):

    Questioncount = 0

    for x in smallset[q]:
        if x == search:
            return Questioncount, smallset['Actuele Opleidingsnaam volgens CROHO'][Questioncount]

        Questioncount += 1


def create_complete_frame(df, question, smallset):
    CompleteFrame = df.copy()

    if len(CompleteFrame.columns) == 1:
        CompleteFrame.columns = ['Question']
        CompleteFrame.insert(0, 'QuestionNumber', range(1, 1 + len(CompleteFrame)))
    else:
        CompleteFrame.columns = ['QuestionNumber', 'Question', 'PositivityScore', 'NegativityScore']

    CompleteFrame['placeholder'] = CompleteFrame['Question'].apply(lambda x: question_search_miner(question, smallset, x))
    CompleteFrame['QuestionNumber'] = CompleteFrame['placeholder'].str[0]
    CompleteFrame['Academie'] = CompleteFrame['placeholder'].str[1]
    CompleteFrame = CompleteFrame.drop('placeholder', axis=1)
    CompleteFrame['PositivityScore'] = CompleteFrame['Question'].apply(lambda x: question_positivity_score(x))
    CompleteFrame['NegativityScore'] = CompleteFrame['Question'].apply(lambda x: question_negative_score(x))

    return CompleteFrame


def plot_creater(dfset, question):
    positivityscore = positivity_rating(dfset)
    negativityscore = negativity_rating(dfset)

    size = [positivityscore, negativityscore]
    labels = 'Positive', 'Negative'
    total = positivityscore + negativityscore
    explode = (0.1, 0.1)

    fig, ax = plt.subplots()
    fig.set_size_inches(5, 2)
    fig.set_facecolor('#010409')

    ax.pie(size, labels=labels, autopct=lambda p: '{:.0f}'.format(p * total / 100),
           colors=['#C20030', '#555555'], shadow=True, startangle=90, explode=explode)

    ax.set_title(question)

    return fig


def academy_plot_creater(Academieframe, x):
    a = Academieframe["Beantwoord_Pos"].sum()
    b = Academieframe["Beantwoord_Neg"].sum()
    c = Academieframe["Beantwoord_Mix"].sum()
    d = Academieframe["Beantwoord"].sum()
    abc = d - a - b - c

    size = [a, b, c, abc]
    labels = 'Positive', 'Negative', 'Mixed', 'Neutral'
    explode = (0.3, 0.5, 0.5, 0.05)

    plt.pie(size, labels=labels, autopct='%1.0f%%', shadow=True, startangle=90, explode=explode, colors=['g', 'r', 'b', 'grey'])

    plt.title(x)

    return plt


def create_academy_frame(compframe, smallset, question):
    academielog = compframe['Academie'].unique()

    acframe = pd.DataFrame(columns=['Academie', 'Positivity', 'Negativity', 'Beantwoord', 'Beantwoord_Pos', 'Beantwoord_Neg', 'Beantwoord_Mix'])
    counter = 0

    for x in academielog:
        beantwoord = question_answered(x, smallset, question)

        Row = [x,
               compframe[compframe["Academie"] == x]["PositivityScore"].sum(),
               compframe[compframe["Academie"] == x]["NegativityScore"].sum(),
               beantwoord,
               len(compframe.loc[(compframe["PositivityScore"] > 0) & (
                   compframe["Academie"] == x) & (compframe["NegativityScore"] == 0)]),
               len(compframe.loc[(compframe["NegativityScore"] > 0) & (
                   compframe["Academie"] == x) & (compframe["PositivityScore"] == 0)]),
               len(compframe.loc[(compframe["PositivityScore"] > 0) & (compframe["Academie"] == x) & (compframe["NegativityScore"] > 0)])]

        acframe.loc[counter] = Row
        counter += 1

    return acframe


def question_answered(academie, smallset, question):

    count = 0
    questioncount = 0

    for x in smallset[question]:
        notnan = x
        if notnan == notnan and academie == smallset["Actuele Opleidingsnaam volgens CROHO"][count]:
            questioncount += 1
        count += 1

    return questioncount


def full_academy_visualiser(academieframe):
    for x in academieframe.iterrows():
        plt.subplot(1, 2, 1)

        a = x[1].Beantwoord_Pos
        b = x[1].Beantwoord_Neg
        c = x[1].Beantwoord_Mix
        d = x[1].Beantwoord
        abc = d - a - b - c

        size = [a, b, c, abc]
        labels = 'Positive', 'Negative', 'Mixed', 'Neutral'
        explode = (0.3, 0.5, 0.5, 0.05)

        plt.pie(size, autopct='%1.0f%%', startangle=90, explode=explode, colors=['g', 'r', 'b', 'grey'])
        plt.legend(labels, loc="best")
        plt.title(x[1].Academie)

        plt.subplot(1, 2, 2)

        a = x[1].Positivity
        b = x[1].Negativity

        size = [a, b]
        total = a + b
        explode = (0.1, 0.1)

        plt.pie(size, autopct=lambda p: '{:.0f}'.format(p * total / 100), colors=['g', 'r'], shadow=True, startangle=90, explode=explode)

        plt.title("Comparison")

        plt.show()


def get_bigram_grid(df):
    newdf = pd.DataFrame(df)
    newdf.columns = ['question']

    stopping = stopwords.words('dutch')

    c_vec = CountVectorizer(stop_words=stopping, ngram_range=(2, 3))
    ngrams = c_vec.fit_transform(newdf['question'])
    count_values = ngrams.toarray().sum(axis=0)
    vocab = c_vec.vocabulary_
    df_ngram = pd.DataFrame(sorted([(count_values[i], k) for k, i in vocab.items()], reverse=True)
                            ).rename(columns={0: 'frequency', 1: 'bigram'})

    return df_ngram
