## Human-In-The-Loop Data Annotation Tool using Active Learning Model

Welcome! This project is a self-contained textual data annotation tool that uses machine learning to make label predictions.

The Process is simple:
1. Start by using the simple sentence parser that extracts sentences from your data. Just paste your text into the text box.
2. You create the tags you want to label with, such as "positive" or "negative" for sentiment analysis for instance.
3. Manually label a subset of the dataset. You don't need to label each word!
4. Create a model, which will train on the data you have labelled.
5. Finally, you can select the senetences you want automatically labelled, and let the tool do the work!
6. You simply make corrections as needed, and can continue re-training the active learning model based on your fixes.

### Dependencies
* Python
* TensorFlow
* Numpy
* SciPy
* Flask


### [User Manual](https://github.com/RyanTonerCode/Data-Annotation-Tool-With-Active-Learning/blob/main/Data%20Annotation%20Tool%20User%20Manual.docx)
