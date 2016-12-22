# DM_BD_Project2016
> URL Categorization

## Description
### 1 - Collecting data
In this step we generate a dataset compose by tweets whith geolocation. This dataset is divided in two :

1. Tweets with GPS coordinates
2. Tweets with related to a place

These two set are stored in 'step1_collectingData/dataset_coordinates' and 'step1_collectingData/dataset_places'.

## Structure
### Step 1 - Collecting data
- **collectTweets.py** : Is a Python script used for collecting tweets and make the dataset
- **parseTweets.py** : Is a Python script used for compress tweets collected by 'CollectTweets.py'
- **~~changeStatusToJson.py~~** : TODO, it should transform files in 'Old' into a json file
- **dataset_coordinates** : Folder that contain tweets with geolocation
  - **Old** : Folder that contain tweets in a different format (Not Json)
  - **reduced_json** : Folder that contain tweets compressed by 'ParseTweets.py'
- **dataset_places** : Folder that contain tweets without geolocation, but refferred to a place
  - **Old** : Folder that contain tweets in a different format (Not Json)
  - **reduced_json** : Folder that contain tweets compressed by 'ParseTweets.py'
