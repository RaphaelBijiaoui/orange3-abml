import pickle
import Orange
from Orange.evaluation import TestOnTestData, CA, AUC, LogLoss
import orangecontrib.evcrules.logistic as logistic
import orangecontrib.abml.abrules as rules
import orangecontrib.abml.argumentation as arg

# settings
optimize_penalty = False # do this only once, then set the value as fixed
cycle = 0

# create learner
rule_learner = rules.ABRuleLearner(add_sub_rules=True)
rule_learner.evds = pickle.load(open("evds.pickle", "rb"))
learner = logistic.LRRulesLearner(rule_learner=rule_learner)

# load data
data = Orange.data.Table('learndata')

if optimize_penalty:
    l1 = logistic.LRRulesLearner(opt_penalty=True)
    print("Best penalty is: ", l1.penalty)
learner.penalty = 1 # result of optimization

# learn a classifier
classifier = learner(data)

# save model
print(classifier)
fmodel = open("model.txt".format(cycle), "wt")
fmodel.write(str(classifier))

# test model + other methods
testdata = Orange.data.Table('testdata')
bayes = Orange.classification.NaiveBayesLearner()
logistic = Orange.classification.LogisticRegressionLearner()
random_forest = Orange.classification.RandomForestLearner()
svm = Orange.classification.SVMLearner()
cn2 = Orange.classification.rules.CN2UnorderedLearner()
learners = [learner, logistic, bayes, cn2, random_forest, svm]
res = TestOnTestData(data, testdata, learners)
ca = CA(res)
auc = AUC(res)
ll = LogLoss(res)

names = ['logrules', 'logistic', 'naive-bayes', 'cn2', 'random-forest', 'svm']
scores = ""
scores += "CA\tAUC\tLogLoss\tMethod\n"
for ni, n in enumerate(names):
    scores += "{}\t{}\t{}\t{}\n".format(ca[ni], auc[ni], ll[ni], n)
print(scores)
fscores = open("scores.txt", "wt")
fscores.write(scores)

# find critical examples
c, indices = arg.find_critical(learner, learner.rule_learner, data)

for i in range(1, 6):
    ind = indices[-i]
    print("Criticality: ", c[ind], "index: ", ind)
    print(data[ind])


