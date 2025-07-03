<div align="center">
    <img src="static/img/logo.png" width="128" height="128">
    <h1>Fit-Fuel</h1>
</div>
<div align="center">
  <p>
    Fit-Fuel is a Django powered website built for a food business to provide its customers the ability to order online.
    Django backend allows for easy and on-the-spot menu adjustments and order tracking, while payment is handled with Stripe.
  </p>
  <p>
    You can visit the live website <a href="www.rep-talk.com">here
  </p>
</div>

<h2>Website Details</h2>

The primary focus of the website is in the menu manipulation and payment processing. Menu items can be edited in the Django
administration panel via the superuser account:

![image](https://github.com/user-attachments/assets/a5cff7ba-7d20-4789-96a1-1287dcf491d5)

If you want to check this out yourself, you can log in as the superuser by using the following credentials:
- Username: **superuser**
- Password: **superuser**

The admin panel allows us to easily create new categories for items, adjust their details, create different portions and provide a discount.
Macro displays on the items themselves are calculated live using JavaScript, the superuser just needs to provide the baseline for 100g.

As for the payment it is implemented using a Stripe test account. The system works by utilizing a websocket on Stripe and creating the method
that will run when that event occurs, in this case the event being the successfull payment. If you want to test out the payment, you can use
the test-card that Stripe provides:
- Card number: **4242 4242 4242 4242**
- Expiery Date: **Anything after the current day**
- CVC: **Any 3 number combination**

![image](https://github.com/user-attachments/assets/46951927-d561-49d9-81f2-619409b99d10)

<div align="center">Orders are created after the payment is deemed successfull and they can be viewed in the admin panel as well. Each order has the required customer
data as well as all items that the customer ordered in JSON format.</div>

<h2>👤 Account System</h2>

Users can make accounts and save their personal information for future orders. On their profile, they can also view any past order they made as well as look at a chart
depicting the macros they have taken in from the food they ordered from the website. Users can order without an account as well, however their information isn't stored
in this case. All of this is built in Django using a Custom User model and all of the functionality lies in the 'users' app.

<h2>🛒 Cart Feature</h2>

I have implemented a pop-up cart into the website, which customers can use to quickly view what they added as well as remove stuff that they do not want in the cart. The cart
itself is implemented with Bootstrap's Popover element and its functionality is implemented in JavaScript. The cart holds a checkout button, which will redirect users
to the checkout page. The cart is a part of the header element, meaning it is accessible in all areas of the website. It uses the 'localStorage' to get its data which means
a cart will be remembered for any specific user until they modify it or make an order.

<h2>🌐 Frontend</h2>

The frontend is built by HTML, JS and custom CSS. The styling is powered by **SAAS**, which means the main styles.css files is generated dynamically and compressed to reduce its size.
Website is optimized for all devices as well using custom media queries. The structure of the layout is done using **'Flexbox'** and **'CSS Grid'**, two most modern ways to create designs.
HTML is structured using the BEM notation, making it easy to read and expand. CSS is a bit complex, I wanted to show what I know when it comes to styling as well as proper structuring.
During development, I used the 'live-server' extension to speed up my workflow on the frontend part.
