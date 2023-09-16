 # Strava Social Media API

API for Strava, focusing on social media. It is using Selenium web-scraper. Use it to follow, unfollow, give kudos, comment, get a kudos list, download GPX files, and more.
You can just import a Strava_API class or a Strava_Bot that uses the API to make some commands. Or just use Strava_Bot as an example for your personal bot

# Strava_API


## Features:

Commands to get a list of:
* Users who follow a person
* Uers that  person is following
* Person who gave kudos on the activity
* Activities from a user

Commands to:
* Follow a user
* Unfollow a user
* Comment on activity
* Like activity
* Download activity GPX file

## Basic Usage

#### PIP INSTALL
```
Run -> pip install StravaSocialAPI <- in command window to install the lybrary
```

#### IMPORT CLIENT
```
from StravaSocialAPI import Client
cl = Client()
```
Default attributes:

* headless = False -> Turn to True if you want to hide the browser. BROKEN: It may not find some elements to interact!
* sleep_for_page_to_load = 1 -> time on how long it waits for elements to be loaded. Used when calling (By.Xpath) since there is ussualy more than one element to be loaded.

 
#### LOGIN
```
cl.login(email, password)
```

#### SOCIAL MEADIA COMMANDS
You can get the user's ID on the home page and copying the last number from the link:
https://www.strava.com/pros/6021015
```
pogacar = '6021015'

cl.follow(user_id = pogacar)
cl.unfollow(user_id = pogacar)
```

```
cl.get_followers_list(user_id = pogacar)
```
Default attributes:
* max_limit_of_ids = 100000 -> Max limit has to be set to exit the while loop. If the user has fewer followers than argument, the function will still exist and will return the list.

```
cl.get_activity_ids_from_user(user_id = '37528897')
```
Default attributes:
* num_of_ids = 10000 -> number on how many ID's you want from a user
* max_months_to_scrape = 100 -> Max number of months to search for ID's. If 'num_of_ids' is higher than the total number of activities the user has, we have to stop searching with this limit.

```
cl.get_kudos_list_from_activity(user_id = '9419737987')
```
We cannot collect all user's ID's with this method, only a limited amount that the Strava website allows. 

```
cl.like_activity(activity_id = '9790149320')
```
If an activity is already liked, the method likes it again. Result in no change or errors.

```
cl.comment_on_activity(activity_id = '9790149320', comment = "Good job! :)")
```

```
cl.download_gpx_files(activity_id_list = ['9419737987','9790149320'], destination_directory = 'D:\Dokumenti\Python\GPX', download_directory = 'D:\Prenosi', wait_for_dowload_s = 5)
```
Attributes description:
* activity_id_list -> You have to input an array of ids. If you want to download just one, use; ['9419737987']. The array is needed because we have to wait for the activity/s to download before we can move them. If the internet speed is slow, increase the 'wait_for_dowload_s' .
* destination_directory -> You have to input the destination directory, where the downloaded GPX files will be moved.
* download_directory = 'D:\Downloads' -> define your defoult dowload direktory. It can have a different name if your OS is in a different language or if you use MacOS or Linux.
* wait_for_dowload_s = 5 -> time that we wait for the last download to finish. Set it higher if you have slower internet.


# Strava_Bot
Check the Strava_Bot module to see the usage of the API
