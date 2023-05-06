To start app run following commands:
1] pip install -r requirements.txt
2] python app.py OR just press Run button in replit



=====================================
# python "./FlashCard_WebApp/app.py"
=====================================


This is a final project for MAD-I

• Project Files Tree Structure is as follows :
.\code\
│
├── application\
│   ├── api.py
│   ├── config.py
│   ├── controllers.py
│   ├── database.py
│   ├── errors.py
│   └── models.py
│
├── databases\
│   ├── dummy.txt
│   └── flashCardDB.sqlite3
│
├── Exports\
│   └── dummy.txt
│
├── Extras\
│   ├── deck_import_A_eng_words.csv
│   ├── deck_import_B_eng_words.csv
│   └── deck_import_C_hindi_eng.csv
│
├── Imports\
│   └── dummy.txt
│
├── static\
│   ├── css\
│   │   ├── addCard.css
│   │   ├── addDeck.css
│   │   ├── dashboard.css
│   │   ├── editCard.css
│   │   ├── editDeck.css
│   │   ├── editDeckData.css
│   │   ├── home.css
│   │   ├── importDeck.css
│   │   ├── login.css
│   │   ├── review.css
│   │   └── signup.css
│   │
│   ├── img\
│   │   └── home_background.png
│   │
│   └── js\
│       ├── dashboard.js
│       ├── flashMessage.js
│       └── review.js
│
│
├── templates\
│   ├── addCard.html
│   ├── addDeck.html
│   ├── dashboard.html
│   ├── editCard.html
│   ├── editDeck.html
│   ├── editDeckData.html
│   ├── flashMessage.html
│   ├── home.html
│   ├── importDeck.html
│   ├── login.html
│   ├── review.html
│   └── signup.html
│
├── app.py
├── current_user.json
├── main.py
├── README.txt
└── requirements.txt

To start Flash-card App, we need to install/upgrade dependencies from requirements.txt file
For that, run command 'pip install -r requirements.txt' without single quotes in Shell.

After all requirements are installed we can start Flash-card App.

To start Flash-card App, run the app.py file.
For that, run command 'python "./FlashCard_WebApp/app.py"' without single quotes in Shell.

After flask server is launched a user can login (if registered) or signup.
Then the dashboard will be visible and user can see the list of decks in dashboard and last reviewed deck will be highlighted in green.

User can perform following functions:
edit a deck
add a card to deck
delete a card
delete a deck
edit deck description
export a deck
import a deck
(and all actions are self explanatory)
