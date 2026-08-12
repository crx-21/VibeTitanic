# Project Overview
Created in order to analyse and predict survival of passengers on the Titanic. 
We will create an model that predicts if a passenger survived or not. The model will use the training data to learn the patterns and then use that to predict the survival of the passengers in the test data.
After that we will use it to predict whether the other 418 passengers on board survived or not.
When it's done predicting it will give us an CSV with a table two collumns PassengerID and Survived (0 and 1)

# Git Rules
Before starting to work always pull any changes on main to be up to date. Afterwards create a suggestive branch for your work.
Move to the branch and start working. After every small implementation an subagent will check for errors in code or at runtime. If errors are found review the code and fix it. If everything is well push on the branch and create a first pull request if the branch does not have one. This will continue after each implementation until the feature is fully implemented. Afterwards another subagent will test and analyse the results given by the model and provide feedback on how to improve the model and what's next.

Manage your subagents you will decide what gets pushed to the branch.
If you decide to create a PR it must contain suggestive title to define quickly what's going on eg. [Test] for testing, [Feature] for feature etc..

You are not allowed to push to main.
# Tech Stack
- Language: Python 3.10+
- Data Analysis: Pandas, numpy
- Visualization: Matplotlib / Seaborn
- Machine Learning: xgboost

