AuctionHouse

- A full-stack database-driven web application built for a databases course project. AuctionHouse is a simple online auction platform where users can list items for auction, place bids, and view live countdowns on active listings.

Live Site: tonystonedb.pythonanywhere.com

--------------------------------------------

Tech Stack:

LayerTechnologyBackendPython 3.13, 
FlaskFormsFlask-WTFDatabaseSQLite via Flask-SQLAlchemyFrontendHTML, 
CSS, JavaScript, Hosting, PythonAnywhere (free tier).


--------------------------------------------


Features

* Browse all open auctions on the home page.

* Filter listings by category (Electronics, Clothing, Collectibles, Books, Sports, Other).

* Create a new auction listing with a title, description, starting price, category, and end time.

* Place bids on open items — bid validation ensures every new bid must beat the current highest price.

* View full bid history on each item detail page.

* Manually close an auction that reveals the winner and final price.

* Live countdown timer on every auction card and item detail page, updating every second in real time using JavaScript.


--------------------------------------------


Database Design:


- The database consists of 4 tables normalized to 3NF.

User:

  * Stores all users who interact with the platform — both sellers and bidders.

  * Primary key: id
  * Referenced by Item.seller_id and Bid.bidder_id

--------

Category:

  * A lookup table that keeps category names normalized — prevents repeating strings across every item row.

  * Primary key: id
  * Referenced by Item.category_id


---------

Item:

Represents each auction listing. Stores the title, description, starting price, end time, and status.

  * Primary key: id
  * Foreign key: seller_id → User.id (the user who created the listing)
  * Foreign key: category_id → Category.id (the category this item belongs to)

---------

Bid: 

Records every bid placed on an auction. Acts as a junction between the User and the Item.

  * Primary key: id
  * Foreign key: item_id → Item.id (the auction this bid was placed on)
  * Foreign key: bidder_id → User.id (the user who placed the bid)
