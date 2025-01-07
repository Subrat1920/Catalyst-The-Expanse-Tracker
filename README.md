# Catalyst-The Expanse Tracker
###### Catalyst is a comprehensive expense tracking web application designed to help users monitor their financial activities effortlessly. Built with modern web technologies, Catalyst provides an intuitive interface and insightful graphical representations, enabling users to make informed financial decisions. With a focus on simplicity and functionality, Catalyst empowers individuals to track and analyze their expenses over a three-month period.

### Features
  User-Friendly Interface: Simple and intuitive design for seamless expense tracking.
  Data Visualization: Interactive charts and graphs to help users understand spending patterns.
  Custom Expense Categories: Flexibility to categorize expenses for detailed insights.
  Three-Month Overview: Monitor and compare financial data over three months.
  Secure and Scalable: Built using robust backend and secure database management.

### Technologies Used
#### Frontend:
  HTML, CSS, Bootstrap, JavaScript for responsive and dynamic user interfaces.
#### Backend:
  Python and Django for server-side logic and efficient data handling.
#### Database:
  PostgreSQL for reliable and scalable data storage.

### How to Use Catalyst
  Sign Up/Log In: Create an account to securely access your expense tracker.
  Add Expenses: Log daily expenses with custom categories and descriptions.
  View Insights: Access interactive graphs for a clear understanding of spending habits.
  Track Progress: Monitor financial trends over the selected period and adjust budgets.

## How to clone the app
###### In order to clone the app follow the following steps
  1. Open Terminal and enter the terminal code :
     ###### git clone git@github.com:Subrat1920/Catalyst-The-Expanse-Tracker.git
  2. Activate Virtual Environemnt :
     ###### venv\Scripts\activate
  3. Install the required packages :
     ###### pip install -r requirements.txt
  4. Check for the migrations :
     ###### python manage.py showmigrations
  5. Migrate the dependencies :
     ###### python manage.py migrate
  6. Make migrations :
      ###### python manage.py makemigrations
  7. Make a super-user for admin panel controll :
      ###### python manage.py createsuperuser
  8. Give the required option to the terminal
  9. Run the server :
      ###### python manage.py runserver
        
