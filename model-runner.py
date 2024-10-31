#!/usr/bin/env python3

import ast
import numpy as np
import pandas as pd
import argparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import warnings
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier


warnings.filterwarnings("ignore")


def load_data(target: str, file: int) -> tuple:
    data = pd.read_csv(f'tdl/all-files-with-100-pcaps-with-{file}-packets.csv')
    data = data.drop(columns=['Unnamed: 0'])
    labels = data.pop('label')
    data = data.to_numpy()
    labels = labels.iloc[:].values
    # print unique labels and their counts
    unique, counts = np.unique(labels, return_counts=True)
    # print(dict(zip(unique, counts)))

    with open('tdl/label_counts.txt', 'w') as f:
        print(dict(zip(unique, counts)), file=f)
    new_data = []
    for tdl, label in zip(data, labels):
        if target in ['browser', 'os']:
            if label % 2 == 0:
                continue
        new_data.append([ast.literal_eval(j) for j in tdl])
    if target == 'pqc':
        labels = np.array([i % 2 for i in labels])
    elif target == 'browser':
        labels = np.array([((i // 10) % 10) * 10 for i in labels if i % 2 == 1])
    elif target == 'os':
        labels = np.array([(i // 100) * 100 for i in labels if i % 2 == 1])
    elif target == 'all':
        labels = np.array([i for i in labels]) #])
    data = np.array(new_data)
    data = np.array([i.flatten() for i in data])
    return data, labels


def run_and_organize(data, idx, labels, model, model_names, results):
    skf = StratifiedKFold(n_splits=10)
    accuracy = cross_val_score(model, data, labels, cv=skf, scoring='accuracy')
    precision = cross_val_score(model, data, labels, cv=skf, scoring='precision_weighted')
    recall = cross_val_score(model, data, labels, cv=skf, scoring='recall_weighted')
    f1 = cross_val_score(model, data, labels, cv=skf, scoring='f1_weighted')
    auc = cross_val_score(model, data, labels, cv=skf, scoring='roc_auc_ovr')
    # 2 decimal places for results
    acc_res = f'{accuracy.mean():.2f} +/- {accuracy.std():.2f}'
    prec_res = f'{precision.mean():.2f} +/- {precision.std():.2f}'
    rec_res = f'{recall.mean():.2f} +/- {recall.std():.2f}'
    f1_res = f'{f1.mean():.2f} +/- {f1.std():.2f}'
    auc_res = f'{auc.mean():.2f} +/- {auc.std():.2f}'
    results.loc[len(results)] = [model_names[idx], acc_res, prec_res, rec_res, f1_res, auc_res]


def run_models(target: str, amount: int) -> None:
    data, labels = load_data(target, amount)
    print(labels)
    labels = LabelEncoder().fit_transform(labels)
    print(labels)

    x_train, x_test, y_train, y_test = train_test_split(
        data,
        labels,
        test_size=0.1,
        random_state=42,
        stratify=labels
    )
    # random forest
    clf = RandomForestClassifier(n_estimators=1, random_state=0)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    print("Random Forest")
    print(classification_report(y_test, y_pred))

    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    print("Decision Tree")
    print(classification_report(y_test, y_pred))

    # dataframe of results: model, accuracy, precision, recall, f1, auc
    # list 10 classifiers to test, for each use stratified kfold with 10 splits
    # save results to csv
    # use cross_val_score for each classifier
    models = [
        RandomForestClassifier(),
        XGBClassifier(),
        LogisticRegression(),
        KNeighborsClassifier(),
        DecisionTreeClassifier(),
        MLPClassifier(),
        GaussianNB(),
        AdaBoostClassifier(),
        GradientBoostingClassifier()
    ]
    model_names = [
        'Random Forest',
        'XGBoost',
        'Logistic Regression',
        'KNN',
        'Decision Tree',
        'MLP',
        'Naive Bayes',
        'AdaBoost',
        'Gradient Boosting'
    ]
    # sort models alphabetically
    model_names, models = zip(*sorted(zip(model_names, models)))

    results = pd.DataFrame(columns=[
        'Model',
        'Accuracy',
        'Precision',
        'Recall',
        'F1-score',
        'AUC'
    ])
    for idx, model in enumerate(models):
        run_and_organize(data, idx, labels, model, model_names, results)
    results.to_csv(f'ICC/new-{target}-with-{amount}-packets-results.csv')


def main() -> None:
    targets = ['all', 'pqc', 'browser', 'os']
    packets = [1, 5, 10, 15, 20]
    for target in targets:
        for amount in packets:
            run_models(target, amount)


if __name__ == "__main__":
    main()

