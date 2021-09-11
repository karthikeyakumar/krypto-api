# krypto-api

  ##   Language used
- ##Python
### Libraries used
-  Flask
- Requests
- flask_sqlalchemy
- functools 
- uuid
- Pyjwt

# Process
1. Install the Libraries mentioned above  and run app.py
2.  from local host move /login in postman use basic-auth with details { login : admin  ,Password: 8101}
3. get the jwt token for above response
4. use that token to make header in postman x-acces-tokens: {token u got from login reponse}
5. move to /alert/create to create the new alert
6. To see all alerts move to alerts/all in databse created by user
7. To delete the alert move to /alert/delete/(alert-id)  to delete the alert

## Email -Notifier
- Run temp.py seperately to monior the price of bitcoin and send email to users.


