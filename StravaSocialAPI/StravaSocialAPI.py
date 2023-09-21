import os
import shutil
import glob
import sys
import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from time import sleep
from datetime import datetime

def print_progress(episode: int, num_episodes: int, name_of_operation:str = None ):
    completed = int(episode/num_episodes * 20)
    remaining = 20 - completed - 1
    progress = "[" + "-"*completed + ">" + "-"*remaining + "]"
    print("\r", progress, end=f" Progress of {name_of_operation} : {int (episode/num_episodes*100) }% , Collected: {episode} ")

def handle_too_many_requests(func):
    """
    This function wrapps any argument with with code
    In this case with try/except to catch to many request.
    The only way to see if we made to many request is to go to home-page of  Strava
    If we can't do that we are blocked
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TimeoutException:
            print("Time-out exception ")
            try:
                self = args[0]  # Assuming the first argument is always 'self'
                self.driver.get('https://www.strava.com/login')
                print("Tried to acces home-page")
            except:
                sys.exit("Can't visit home page. You have made to many request and are blocked")
            
    return wrapper

class Client:
    def __init__(self, headless=False, sleep_for_page_to_load = 1):
        self.sleep_for_page_to_load = sleep_for_page_to_load
        self.options = webdriver.EdgeOptions()

        if headless:
            self.options.add_argument('--headless')         # if you use headless mode, some buttons can't be used
        self.options.add_argument('--log-level=3')          #Disable warnigs from web console
        self.driver = webdriver.Edge(options=self.options)  #apply options
        self.driver.maximize_window()                       # Some buttons can't be located if the window is not maximized
        os.system('cls' if os.name == 'nt' else 'clear')    #clear console
        
    #------------------------------Every method with _ is private. Meant to be used only in this class----------------------------------
    
    @handle_too_many_requests
    def __click_by_id(self, id_name:str, wait_time=10):
        """
        Click a button that has 'id' element
        """
        wait = WebDriverWait(self.driver, wait_time)
        login_button = wait.until(EC.element_to_be_clickable((By.ID, id_name)), message="Couldn't find the button. Try using to disable headles mode or maximize the window " )
        login_button.click()
        
    @handle_too_many_requests   
    def __click_buttons_xpath(self, xpath: str):
        """
        Collects all matching elements using the given XPath expression and tries to click them.
        Return bool value if successful click
        """
        
        #Get button/s
        buttons = self.driver.find_elements(By.XPATH, xpath)
        
        #XPATH can give you more than one button, not all are click-able
        try:
            for button in buttons:
                button.click()
                return True
        except ElementClickInterceptedException:
            pass #just ignore the un-click-able buttons
        return False
            
    @handle_too_many_requests
    def __insert_text_by_id(self, id_name: str, text: str):
        """
        Insert text into field that has 'id'
        """
        box = self.driver.find_element(By.ID, id_name)
        box.send_keys(text)   
        
    @handle_too_many_requests
    def __follow_unfollow(self, id_num: str, action: str):
        """ 
        Generalized method that follows or follows user, based on the 'action' argument 
        """
        
        try:
            self.driver.get('https://www.strava.com/athletes/' + id_num )
            button = WebDriverWait(self.driver, 5).until( EC.presence_of_element_located((By.CLASS_NAME, action) ))
            button.click()
            print(f"{action}ed {id_num}")
        except TimeoutException:
            print(f"The {action}' button was not found within the given timeout period.")
        except Exception as e:
            print("Unknown error:", e)
        finally:
            return 0
        
    @handle_too_many_requests
    def __collect_users_ids(self, user_id: int, max_limit_of_ids: int):
        """
        Private method to collect user's following or followers ID's
        """
        athlete_ids = []
        while True:
            wait = WebDriverWait(self.driver, 10)
            #go down the classes until you hit the IDs
            follow_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'js-follow-container')))
            following_list_container = follow_container.find_element(By.CLASS_NAME, 'tab-content')
            athlete_list = following_list_container.find_element(By.CLASS_NAME, 'list-athletes')
            athlete_elements = athlete_list.find_elements(By.TAG_NAME, 'li')

            # Extract the data-athlete-id attributes
            for athlete_element in athlete_elements:
                athlete_id = athlete_element.get_attribute('data-athlete-id')
                athlete_ids.append(athlete_id)   
                    
            #print progres
            print_progress(len(athlete_ids), max_limit_of_ids, 'collecting IDs')   
            
            #Try and click the next button to load new data
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
                next_button.click()
            except NoSuchElementException:
                #Excit the while loop
                break
           
            if(len(athlete_ids) >= max_limit_of_ids): break
                   
        print(f"Collected {len(athlete_ids)} IDs ")
        return athlete_ids
    
    @handle_too_many_requests
    def __collect_activities_ids(self, to_scrape_link: str):
        """
        Collects ID's from an activity id and returns them
        """
        
        self.driver.get(to_scrape_link)
        
         #Since the client searches elemets, we can't wait to load a 
         #specific element, so sleep best option to wait that page load
        sleep(self.sleep_for_page_to_load)
        
        #locate elements with ancor 'a'. 'href' and 'activities'
        try:
            activities = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/activities/")]')
        except StaleElementReferenceException:
            print('Elemets couldnt be found. Page may have loaded to slowly. Try and incresing the clients "sleep_for_page_to_load" to a bigger value. Current value: ', self.sleep_for_page_to_load , "s")
            return 0
        activity_ids = []
        for activity in activities:
            #grab the activity under 'href' and split the link
            activity_ids.append( activity.get_attribute('href').split('/')[-1].split('#')[0] )

        #remove duplicates 
        return list(set(activity_ids))
      
    @handle_too_many_requests
    def login(self, mail: str, password: str):
        """
        Logs into your Strava accoun
        """
        
        self.driver.get('https://www.strava.com/login')
        self.__insert_text_by_id('email', mail)
        self.__insert_text_by_id('password', password)
        self.__click_by_id('login-button')

        # Check for the error message
        sleep(3) 
        error_message = None
        try:
            error_message = self.driver.find_element(By.CLASS_NAME, 'alert-message').text
            if error_message:
                print("Error message!: ", error_message)
                return
        except:
            #no error message could be found
            print('Login succesfull! ') 

    @handle_too_many_requests
    def follow(self, user_id: str):
        """
        Follow a user. If already following the action is ignored
        """
        self.__follow_unfollow(user_id, 'follow')
        
    @handle_too_many_requests       
    def unfollow(self, user_id: str):
        """
        Unollow a user. If you don't follow the user, the action is ignored
        """
        self.__follow_unfollow(user_id, 'unfollow')
       
    @handle_too_many_requests       
    def get_following_list(self, user_id: str, max_limit_of_ids:int = 10000):
        """
        Get list of ids, that the user specified, is following. 
        """

        self.driver.get('https://www.strava.com/athletes/' + user_id + '/follows?type=following')
        return self.__collect_users_ids(user_id, max_limit_of_ids)
 
    @handle_too_many_requests
    def get_followers_list(self, user_id: str, max_limit_of_ids: int = 10000):
        """
        Get a list of IDs that are following the specefied user
        """
        self.driver.get('https://www.strava.com/athletes/' + user_id + '/follows?type=followers')
        return self.__collect_users_ids(user_id, max_limit_of_ids)     
    
    @handle_too_many_requests
    def get_activity_ids_from_user(self, user_id: str, num_of_ids:int = 10000 , max_months_to_scrape: int = 1000 ):
        """
        Collect activities IDs from a specific user 
        """
        def __get_interval(): 
            """
            Returns a int interval corresponding to current month and year separate. 
            Later we decrease the month by -1, so we return separately year and month
            """
            #We add '0' between year and month if the month is lees than 10 
            if month < 10:
                return ( str(year * 10) + str(month) ) 
            else:
                return  ( str(year) + str(month) )  
            
        def __lower_interval(year: int, month: int):
            month -= 1
            
            if month < 1:
                month = 12
                year -= 1
             
            return year, month
        
        def __remove_invalid_activity_ids(ids_list):
            """
            Delete all IDs that are invalid: any longer than 10 digits
            """
            valid_ids = []
            for _id in ids_list:
                if len( list(_id) ) == 10:
                    valid_ids.append(_id)                   
            return valid_ids
        
                    
        #get current year and month. We change these values to get acivities in another page 
        now = datetime.now()
        year = now.year
        month = now.month

        months_scraped = 0
        activities_ids = []
        while True:
            interval = __get_interval()
            to_scrape_link = (
                'https://www.strava.com/athletes/' +
                str(user_id) +
                '#interval?interval=' +
                interval +
                '&interval_type=month&chart_type=miles&year_offset=0'
            )      
            #Collect IDs and again remove duplicates -> sometimes it collects 4 or 5 the same activities under 'Achievements'
            activities_ids.extend(self.__collect_activities_ids(to_scrape_link) )
            activities_ids = list(set(activities_ids))            

            #lower interval by 1 month 
            year, month = __lower_interval(year, month)
            months_scraped +=1
            
            print_progress(len(activities_ids), num_of_ids, 'activitie IDs' )
            
            #control statemtns to break the while loop
            if len(activities_ids) >= num_of_ids:
                print("Collected the desired amount of IDs: ", num_of_ids)
                break
            elif months_scraped >= max_months_to_scrape: 
                print("Hit the limit 'max_months_to_scrape:' ", max_months_to_scrape)
                break
            
        #remove ids with more than 10 digits
        return __remove_invalid_activity_ids(activities_ids)
        
    @handle_too_many_requests        
    def get_kudos_list_from_activity(self, activity_id:str):
        """
        Collects user IDs of those who gave like & comment 
        """
        #Go to activity and search for button
        self.driver.get('https://www.strava.com/activities/' + activity_id)
        kudo_btn = self.driver.find_elements(By.XPATH, ('//button[@data-testid="adp-kudos_button"]') )
        
        #Multiple buttons can be found, but only one works and we click that one
        for button in kudo_btn:
            try:
                button.click()
            except:
                pass
            
        #Neccesery to wait the page to load the list.            
        sleep(self.sleep_for_page_to_load) 
        
        # Calculate the center of the screen
        window_size = self.driver.get_window_size()
        center_x = window_size['width'] // 2
        center_y = window_size['height'] // 2

        # Move the mouse to the center of the screen and scrool down to get al tha data
        ActionChains(self.driver).move_by_offset(center_x, center_y).perform()
        

        elements = self.driver.find_elements(By.XPATH, ('//a[contains(@href, "/athletes/")]') )
        
        #Exctract user IDs
        kudos_user_ids = []
        for element in elements:
            href = element.get_attribute('href')
            kudos_user_ids.append( href.split('/')[-1] )

        #Remove duplicates
        return list(set(kudos_user_ids))   
 
    @handle_too_many_requests  
    def comment_on_activity(self, activity_id: int, comment: str):
        """
        Comments on the specified activity
        """
        #Go to the activity
        self.driver.get('https://www.strava.com/activities/' + activity_id)
        
        #Open list
        self.__click_buttons_xpath('//button[@data-testid="adp-kudos_button"]')
        
        #Click comments
        self.__click_buttons_xpath( '//button[contains(text(), "Comments")]' )
        
        # Find the textarea element and enter text into it
        textareas =  self.driver.find_elements(By.XPATH, '//textarea[@placeholder="Add a comment, @ to mention"]')
        for text_area in textareas:
            try:
                text_area.send_keys(comment)
                self.__click_buttons_xpath('//button[@data-testid="post-comment-btn"]')
                print(f"Commented {comment} on activity {activity_id}")
            except:
                pass

    @handle_too_many_requests     
    def like_activity(self, activity_id: str):
        """
        Gives kudos to the activity, even if had one before
        """
        #Note:-> I choose to open the list of kudos and then give kudos. That way you can give kudos even if you already gave one before
        
        #Go to the activity
        self.driver.get('https://www.strava.com/activities/' + activity_id)
        
        #Open list
        self.__click_buttons_xpath('//button[@data-testid="adp-kudos_button"]')
             
        #Pop-up window takes a lot of time to show. Slep is neccesery
        sleep(self.sleep_for_page_to_load)
            
        if ( self.__click_buttons_xpath( '//button[text()="Give Kudos"]') ): print('Gave kudos to: ', activity_id)
        else: print("Failed to kudos: ", activity_id)

    @handle_too_many_requests     
    def download_gpx_files(self, activity_id_list, destination_directory, download_directory = 'D:\Downloads', wait_for_dowload_s = 5):
        """
        Downloads and moves the GPX files to a folder. Define your defoult download directory; defoult is 'D:\Downloads'
        """
        #Note -> you have to wait X amount for the last GPX file to download before you can move it. 
        #By taking a list of ids as argument and implemetnig for loop for the list, the waiting applies only for the last GPX file


        #Download gpx to defoult downloads
        for i, activity_id in enumerate(activity_id_list):
            self.driver.get('https://www.strava.com/activities/' + activity_id + '/export_gpx')
            #print progres
            print_progress(i+1, len(activity_id_list), 'downloading GPX files:'  ) 
            
        print('\n Finished dowloading GPX files')
        #wait for the last GPX file to download
        sleep(wait_for_dowload_s)

        # Check if the destination directory exists, create it if doesn't
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)
            print('Made a new directory: ', destination_directory)


        num_gpx_moved = 0
        
        while num_gpx_moved < len(activity_id_list):
            # Search for GPX files in the downloads directory
            gpx_files = glob.glob(os.path.join(download_directory, "*.gpx"))

            if not gpx_files:
                print("No GPX file could be found")
                return None

            # Get the newest GPX file
            latest_gpx_file = max(gpx_files, key=os.path.getctime)

            # Get the filename from the GPX file path
            file_name = os.path.basename(latest_gpx_file)
            destination_path = os.path.join(destination_directory, file_name)

            # Check if the file already exists in the destination directory
            if os.path.exists(destination_path):
                # Add a random number to the filename
                file_name = f"{os.path.splitext(file_name)[0]}_{random.randint(1, 9999999)}{os.path.splitext(file_name)[1]}"
                destination_path = os.path.join(destination_directory, file_name)

            # Move the latest GPX file to the destination directory
            shutil.move(latest_gpx_file, destination_path)
            print(f"GPX file '{file_name}' moved to '{destination_directory}'")
            num_gpx_moved += 1
