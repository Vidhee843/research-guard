import os

import joblib
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    accuracy_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

from research_guard.blueprints.research.models import ResearchSession, Publication

"""AI by Jian Wang"""


def train(model_type, research_session: ResearchSession, publications):
    path = f"resources/bucket/{research_session.id}/{model_type}"
    if not os.path.exists(path):
        os.makedirs(path)
    create_data(publications, path)
    if model_type == "naive-bayes-model":
        return train_naive_bayes_model(path)
    elif model_type == "linear-svm-model":
        return train_linear_svm_model(path)
    elif model_type == "random-forest-model":
        return train_random_forest_model(path)
    elif model_type == "logistic-regression-model":
        return train_logistic_regression_model(path)
    else:
        raise ValueError(
            "Invalid type: must be native-bayes-model, linear-svm-model, random-forest-model, or logistic-regression-model."
        )


def create_data(publications: list[Publication], path: str):
    if os.path.exists(path + "/data.joblib"):
        os.remove(path + "/data.joblib")
    data = pd.DataFrame(
        [publication.json for publication in publications if publication.category]
    )
    X = data["abstract"]
    y = data["category"]
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), max_features=2**20, stop_words="english", min_df=3
    )
    X_tfidf = vectorizer.fit_transform(X)
    joblib.dump(vectorizer, path + "/vectorizer.joblib")
    joblib.dump(le, path + "/label_encoder.joblib")
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y_encoded, test_size=0.2, random_state=42
    )
    joblib.dump(
        (X_train, X_test, y_train, y_test),
        path + "/data.joblib",
    )
    del data


def train_naive_bayes_model(path):
    X_train, X_test, y_train, y_test = joblib.load(path + "/data.joblib")
    le = joblib.load(path + "/label_encoder.joblib")
    nb_model = MultinomialNB(alpha=0.05, fit_prior=True)
    nb_model.fit(X_train, y_train)
    y_pred = nb_model.predict(X_test)
    y_test_labels = le.inverse_transform(y_test)
    y_pred_labels = le.inverse_transform(y_pred)
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
    cm_percent = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm_percent,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=le.classes_,
        yticklabels=le.classes_,
        cbar_kws={"label": "Percentage (%)"},
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix (Naive Bayes)")
    plt.tight_layout()
    plt.savefig(path + "/naive_bayes_model.png")
    joblib.dump(nb_model, path + "/naive_bayes_model.joblib")
    return {
        "accuracy": f"{accuracy_score(y_test, y_pred):.4f}",
        "precision": f"{precision_score(y_test, y_pred, average='weighted'):.4f}",
        "recall": f"{recall_score(y_test, y_pred, average='weighted'):.4f}",
        "f1": f"{f1_score(y_test, y_pred, average='weighted'):.4f}",
    }


def train_logistic_regression_model(path: str):
    X_train, X_test, y_train, y_test = joblib.load(path + "/data.joblib")
    le = joblib.load(path + "/label_encoder.joblib")
    lr_model = LogisticRegression(
        solver="saga",
        max_iter=500,
        n_jobs=-1,
        random_state=42,
        multi_class="multinomial",
    )
    lr_model.fit(X_train, y_train)
    y_pred = lr_model.predict(X_test)
    y_test_labels = le.inverse_transform(y_test)
    y_pred_labels = le.inverse_transform(y_pred)
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
    cm_percent = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm_percent,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=le.classes_,
        yticklabels=le.classes_,
        cbar_kws={"label": "Percentage (%)"},
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix (Logistic Regression)")
    plt.tight_layout()
    plt.savefig(path + "/logistic_regression.png")  # Save plot
    joblib.dump(lr_model, path + "/logistic_regression_model.joblib")
    return {
        "accuracy": f"{accuracy_score(y_test, y_pred):.4f}",
        "precision": f"{precision_score(y_test, y_pred, average='weighted'):.4f}",
        "recall": f"{recall_score(y_test, y_pred, average='weighted'):.4f}",
        "f1": f"{f1_score(y_test, y_pred, average='weighted'):.4f}",
    }


def train_linear_svm_model(path: str):
    X_train, X_test, y_train, y_test = joblib.load(path + "/data.joblib")
    le = joblib.load(path + "/label_encoder.joblib")
    linear_svm_model = LinearSVC(C=1.0, random_state=42)
    linear_svm_model.fit(X_train, y_train)
    y_pred = linear_svm_model.predict(X_test)
    y_test_labels = le.inverse_transform(y_test)
    y_pred_labels = le.inverse_transform(y_pred)
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
    cm_percent = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm_percent,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=le.classes_,
        yticklabels=le.classes_,
        cbar_kws={"label": "Percentage (%)"},
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix (Linear SVM)")
    plt.tight_layout()
    plt.savefig(path + "/linear_svm_confusion_matrix.png")
    joblib.dump(linear_svm_model, path + "/linear_svm_model.joblib")
    return {
        "accuracy": f"{accuracy_score(y_test, y_pred):.4f}",
        "precision": f"{precision_score(y_test, y_pred, average='weighted'):.4f}",
        "recall": f"{recall_score(y_test, y_pred, average='weighted'):.4f}",
        "f1": f"{f1_score(y_test, y_pred, average='weighted'):.4f}",
    }


def train_random_forest_model(path: str) -> dict:
    X_train, X_test, y_train, y_test = joblib.load(path + "/data.joblib")
    le = joblib.load(path + "/label_encoder.joblib")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        n_jobs=-1,
        random_state=42,
        class_weight="balanced",
        verbose=0,
    )
    rf_model.fit(X_train, y_train)
    y_pred = rf_model.predict(X_test)
    y_test_labels = le.inverse_transform(y_test)
    y_pred_labels = le.inverse_transform(y_pred)
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
    cm_percent = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm_percent,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=le.classes_,
        yticklabels=le.classes_,
        cbar_kws={"label": "Percentage (%)"},
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix (Random Forest)")
    plt.tight_layout()
    plt.savefig(
        f"{path}/random_forest_confusion_matrix.png", dpi=300, bbox_inches="tight"
    )
    joblib.dump(rf_model, f"{path}/random_forest_model.joblib")
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(
            y_test, y_pred, average="weighted", zero_division=1
        ),
        "recall": recall_score(y_test, y_pred, average="weighted", zero_division=1),
        "f1": f1_score(y_test, y_pred, average="weighted", zero_division=1),
    }


def classify(research_session: ResearchSession, text: str, model_type) -> str:
    nb_model = joblib.load(
        f"resources/bucket/{research_session.id}/{model_type}/{model_type.replace("-", "_")}.joblib"
    )
    le = joblib.load(
        f"resources/bucket/{research_session.id}/{model_type}/label_encoder.joblib"
    )
    vectorizer = joblib.load(
        f"resources/bucket/{research_session.id}/{model_type}/vectorizer.joblib"
    )
    x_input = vectorizer.transform([text])
    y_pred_encoded = nb_model.predict(x_input)
    predicted_category = le.inverse_transform(y_pred_encoded)[0]
    return predicted_category
