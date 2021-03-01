# instapy_stalker
 
 ## The intention is follow users from a third target user, but wisely. 
 
First the script net_db.py downloads and organize who follows who in a two column sqlite database.
Then clinstapy_RPA.py consults this database and actually follows the ones the you don't follow yet, but are followers of your target user. Also unfollow the users that don't follow you back. 
 
 The script need reparametrization of paths and if you change numerical parameters may your instagram account be blocked. 
 the requirement is instapy library and pandas. 
 
 Feel free to make questions, as the script is poorly commented and a bit messy.
