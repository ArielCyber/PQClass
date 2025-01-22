#!/usr/bin/env python3

import argparse
import ast
import warnings

import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder

from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
from sklearn.linear_model import LogisticRegression

from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier


warnings.filterwarnings("ignore")


def load_data(target: str, file: int) -> tuple:
    """
    Load and preprocess data based on the specified target and file.

    :param target: One of 'all', 'pqc', 'browser', or 'os'.
    :param file: Integer indicating the packet count to load.
    :return: Tuple (data, labels) where data is a numpy array and labels is another numpy array.
    """
    # Read CSV and drop unnamed column
    data = pd.read_csv(f'tdl/all-files-with-100-pcaps-with-{file}-packets.csv')
    data = data.drop(columns=['Unnamed: 0'])

    # Separate labels and convert to numpy
    labels = data.pop('label')
    data = data.to_numpy()
    labels = labels.values

    # Log label counts
    unique, counts = np.unique(labels, return_counts=True)
    with open('tdl/label_counts.txt', 'w') as f:
        print(dict(zip(unique, counts)), file=f)

    # Filter out non-PQC samples if target is browser or os
    new_data = []
    for tdl, label in zip(data, labels):
        if target in ['browser', 'os'] and label % 2 == 0:
            continue
        new_data.append([ast.literal_eval(j) for j in tdl])

    # Adjust labels for different targets
    if target == 'pqc':
        # 0 - Not Using PQC
        # 1 - Using PQC
        labels = np.array([i % 2 for i in labels])
    elif target == 'browser':
        # 10 - FireFox
        # 20 - Chrome
        labels = np.array([((i // 10) % 10) * 10 for i in labels if i % 2 == 1])
    elif target == 'os':
        # 200 - Windows
        # 300 - Linux
        # 400 - MacOS
        labels = np.array([(i // 100) * 100 for i in labels if i % 2 == 1])
    elif target == 'all':
        labels = np.array([i for i in labels])

    data = np.array(new_data)
    data = np.array([i.flatten() for i in data])
    return data, labels


def run_and_organize(data, idx, labels, model, model_names, results):
    """
    run_and_organize(data, idx, labels, model, model_names, results)

    Performs stratified 10-fold cross-validation on the given model using the provided
    data and labels. It calculates several performance metrics (accuracy, precision, 
    recall, F1 score, and AUC). The resulting metrics (mean ± standard deviation) are 
    then appended as a new row to the results DataFrame.

    Parameters:
        data (array-like): The input data for training and validation.
        idx (int): Index of the current model in the list of model names.
        labels (array-like): True class labels corresponding to the data.
        model (estimator object): The scikit-learn compatible classifier instance to be evaluated.
        model_names (list of str): List containing the names of available models.
        results (pandas.DataFrame): DataFrame where each row represents metrics for a model.

    Returns:
        None: The results are appended in-place to the provided DataFrame.
    """
    # Use stratified 10-fold cross-validation
    skf = StratifiedKFold(n_splits=10)

    # Collect metrics
    accuracy = cross_val_score(model, data, labels, cv=skf, scoring='accuracy')
    precision = cross_val_score(model, data, labels, cv=skf, scoring='precision_weighted')
    recall = cross_val_score(model, data, labels, cv=skf, scoring='recall_weighted')
    f1 = cross_val_score(model, data, labels, cv=skf, scoring='f1_weighted')
    auc = cross_val_score(model, data, labels, cv=skf, scoring='roc_auc_ovr')

    # Summarize each metric
    acc_res = f"{accuracy.mean():.2f} +/- {accuracy.std():.2f}"
    prec_res = f"{precision.mean():.2f} +/- {precision.std():.2f}"
    rec_res = f"{recall.mean():.2f} +/- {recall.std():.2f}"
    f1_res = f"{f1.mean():.2f} +/- {f1.std():.2f}"
    auc_res = f"{auc.mean():.2f} +/- {auc.std():.2f}"

    # Insert row into results DataFrame
    results.loc[len(results)] = [
        model_names[idx], acc_res, prec_res, rec_res, f1_res, auc_res
    ]


def run_models(target: str, amount: int) -> None:
    """
    Runs multiple classification models on a given dataset.

    This function loads and encodes the data for the specified target label and
    number of packets. It then trains multiple classifiers, evaluates each model's
    performance, and saves the results in a CSV file.

    Args:
        target (str): The label or feature name to predict/classify.
        amount (int): The number of packets or rows to include in the loaded dataset.

    Returns:
        None
    """
    print(f"Running models for {target} with {amount} packets...")
    # Load and encode data
    data, labels = load_data(target, amount)
    labels = LabelEncoder().fit_transform(labels)

    # Estimators and matching names
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

    # Sort models and names
    model_names, models = zip(*sorted(zip(model_names, models)))

    # Prepare results storage
    results = pd.DataFrame(
        columns=['Model', 'Accuracy', 'Precision', 'Recall', 'F1-score', 'AUC']
    )

    # Run each model
    for idx, model in enumerate(models):
        run_and_organize(data, idx, labels, model, model_names, results)

    # Save to CSV
    results.to_csv(f'{target}-with-{amount}-packets-results.csv')


def main() -> None:
    targets = ['all', 'pqc', 'browser', 'os']
    for target in targets:
        run_models(target, 20)


if __name__ == "__main__":
    main()
