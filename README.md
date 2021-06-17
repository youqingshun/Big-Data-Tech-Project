# Big-Data-Tech-Project
## BDT2021
The project contains three folders(i.e. data_preparation, model_fitting, result_display), including all the codes and data.

- data_preprartion folder consists of the data (raw data and processed data) and codes (bike data collecting, car data collecting and weather data collecting codes).
  - These folders or files can be understood via the names.

- model_fitting folder consistes of the first version, last version model building codes and the data frames produced in the process.
  - 1st_dataProcess_ModelBuild.py and last_dataProcess_ModelBuild.py are the first version and last version code to process the data and build the model respectively. 
  - initialData.csv is the data before PCA analysis.
  - trafficData.csv is the data after PCA analysis.
  - weatherData.csv is the data of weather condition.

- result_display folder consists of web system based on python.
  - temp folder contains the html file.
  - main.py contains data preprocessing and logistic regression model.
  - dataProcess_ModelBuild.py is the packaged data processing and other models code.
  - BDT.jason and weatherandtraffic.ibd are the part of trial data.
  - view.py is the code to display the result on a web page.
