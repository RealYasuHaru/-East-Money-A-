东方财富网A股股票数据爬虫项目
项目简介
本项目是一个基于Python的桌面应用程序，用于爬取东方财富网（East Money）的A股股票数据，并将其存储到MySQL数据库中。同时，项目提供了一个图形用户界面（GUI），用于展示数据库中的数据，并支持对数据的增删改查（CRUD）操作。
功能特点
数据爬取
使用Selenium和BeautifulSoup爬取东方财富网的A股股票数据。
支持多页面爬取，用户可以通过GUI输入需要爬取的最大页数。
爬取的数据包括股票代码、名称、价格、涨跌幅、成交量、成交额等信息。
数据存储
使用MySQL数据库存储爬取的数据。
数据库表结构已定义，包含股票的基本信息和交易数据。
提供数据插入、删除、更新和查询的功能。
图形用户界面（GUI）
使用Tkinter库构建GUI，提供用户友好的操作界面。
功能包括：
爬取数据：点击“开始爬取”按钮，启动爬虫并存储数据到数据库。
展示数据：以表格形式展示数据库中的数据。
增删改查：提供添加、删除、编辑和搜索数据的功能。
日志显示：在GUI中显示爬虫运行的日志信息。
数据展示与交互
数据以表格形式展示，用户可以通过表格查看、选择和操作数据。
提供搜索功能，用户可以根据股票代码或名称搜索数据。
支持对选中的数据进行删除、编辑操作。
技术栈
Python：主要编程语言。
Selenium：用于网页自动化爬取。
BeautifulSoup：用于解析HTML页面，提取数据。
MySQL：用于存储爬取的数据。
Tkinter：用于构建图形用户界面。
East Money A-Share Stock Data Scraper
Project Introduction
This project is a desktop application built with Python, designed to scrape A-share stock data from East Money and store it in a MySQL database. It also provides a graphical user interface (GUI) to display the stored data and supports basic CRUD (Create, Read, Update, Delete) operations on the data.
Features
Data Scraping
Uses Selenium and BeautifulSoup to scrape A-share stock data from East Money.
Supports multi-page scraping, allowing users to specify the number of pages to scrape via the GUI.
Scraped data includes stock code, name, price, change percentage, trading volume, turnover, etc.
Data Storage
Stores scraped data in a MySQL database.
The database schema is predefined to include stock information and trading data.
Provides functions for inserting, deleting, updating, and querying data.
Graphical User Interface (GUI)
Built with Tkinter, providing a user-friendly interface.
Features include:
Scraping Data: Click the "Start Scraping" button to initiate the scraper and store data in the database.
Displaying Data: Shows stored data in a table format.
CRUD Operations: Supports adding, deleting, editing, and searching data.
Log Display: Shows scraper logs within the GUI.
Data Display and Interaction
Data is displayed in a table format, allowing users to view, select, and manipulate data.
Provides a search function to find data by stock code or name.
Supports deleting and editing selected data.
Technology Stack
Python: The primary programming language.
Selenium: For web page automation and scraping.
BeautifulSoup: For parsing HTML and extracting data.
MySQL: For storing scraped data.
Tkinter: For building the graphical user interface.
安装与运行
环境依赖
Python：确保已安装Python 3.7或更高版本。
MySQL：确保已安装MySQL数据库，并创建对应的数据库和用户。
Selenium WebDriver：确保已安装Chrome浏览器，并下载对应版本的ChromeDriver。注意事项
ChromeDriver路径
确保chrome_driver_path变量指向正确的ChromeDriver路径。
如果需要，可以将ChromeDriver添加到系统环境变量中。
网络环境
由于爬虫需要访问东方财富网，确保网络环境稳定且能够正常访问目标网站。
数据更新
程序运行时会自动创建数据库表（如果不存在）。如果需要重新爬取数据，建议先清空数据库表。
GUI操作
在GUI中输入爬取页数时，请确保输入的是正整数。
在进行增删改查操作时，请确保已正确选择或输入数据。Installation and Running
Environment Dependencies
Python: Ensure that Python 3.7 or higher is installed.
MySQL: Ensure that MySQL is installed, and the corresponding database and user are created.
Selenium WebDriver: Ensure that Chrome browser is installed, and download the corresponding version of ChromeDriver.Notes
ChromeDriver Path
Ensure that the chrome_driver_path variable points to the correct ChromeDriver path.
Optionally, add ChromeDriver to the system environment variables.
Network Environment
Since the scraper needs to access East Money, ensure that the network environment is stable and can access the target website.
Data Update
The program will automatically create the database table (if it does not exist). If you need to re-scrape data, it is recommended to clear the database table first.
GUI Operations
When entering the number of pages to scrape in the GUI, ensure that it is a positive integer.
When performing CRUD operations, ensure that the data is correctly selected or entered.
