import logging
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import mysql.connector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12315',
    'database': 'a'
}

# Chrome WebDriver path
chrome_driver_path = 'D:/Users/a1984/Desktop/chromedriver-win64/chromedriver.exe'


# Initialize database connection
def init_database():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20),
            name VARCHAR(100),
            price VARCHAR(20),
            change_percent VARCHAR(20),
            change_amount VARCHAR(20),
            volume VARCHAR(50),
            turnover VARCHAR(50),
            amplitude VARCHAR(20),
            highest VARCHAR(20),
            lowest VARCHAR(20),
            open_price VARCHAR(20),
            close_price VARCHAR(20),
            volume_ratio VARCHAR(20),
            turnover_rate VARCHAR(20),
            pe_ratio VARCHAR(20),
            pb_ratio VARCHAR(20)
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        logging.info("数据库表格已创建或已存在")

        return conn, cursor

    except mysql.connector.Error as e:
        logging.error(f"数据库错误: {e}")
        raise


# Insert data into database
def insert_into_database(conn, cursor, data):
    try:
        insert_query = """
        INSERT INTO scraped_data (code, name, price, change_percent, change_amount,
                                  volume, turnover, amplitude, highest, lowest,
                                  open_price, close_price, volume_ratio, turnover_rate,
                                  pe_ratio, pb_ratio)
        VALUES (%(code)s, %(name)s, %(price)s, %(change_percent)s, %(change_amount)s,
                %(volume)s, %(turnover)s, %(amplitude)s, %(highest)s, %(lowest)s,
                %(open_price)s, %(close_price)s, %(volume_ratio)s, %(turnover_rate)s,
                %(pe_ratio)s, %(pb_ratio)s)
        """
        cursor.execute(insert_query, data)
        conn.commit()
        logging.info("数据成功插入数据库")
    except mysql.connector.Error as e:
        logging.error(f"插入数据库错误: {e}")


# Fetch all data from database
def fetch_all_from_database(conn, cursor):
    try:
        select_query = "SELECT * FROM scraped_data"
        cursor.execute(select_query)
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as e:
        logging.error(f"从数据库中获取数据错误: {e}")
        return []


# Delete data from database by ID
def delete_from_database(conn, cursor, id):
    try:
        delete_query = "DELETE FROM scraped_data WHERE id = %s"
        cursor.execute(delete_query, (id,))
        conn.commit()
        logging.info(f"数据 ID {id} 已从数据库中删除")
    except mysql.connector.Error as e:
        logging.error(f"从数据库中删除数据错误: {e}")


# GUI function to display database data in a table
def display_database_data():
    conn, cursor = init_database()  # Initialize database connection
    data_rows = fetch_all_from_database(conn, cursor)
    conn.close()

    # Clear existing table content
    for row in tree.get_children():
        tree.delete(row)

    # Insert fetched data into the table
    for row in data_rows:
        tree.insert('', 'end', values=row)


# GUI function to start scraping
def start_scraping():
    max_pages = int(max_pages_entry.get())  # Get max_pages value from GUI input
    urls = [
        'https://quote.eastmoney.com/center/gridlist.html#hs_a_board',
        'https://quote.eastmoney.com/center/gridlist.html#sh_a_board',
        'https://quote.eastmoney.com/center/gridlist.html#sz_a_board',
        'https://quote.eastmoney.com/center/gridlist.html#bj_a_board'
    ]
    all_scraped_data = []
    conn, cursor = init_database()  # Initialize database connection

    # Clear existing log messages
    log_display.delete(1.0, tk.END)

    for url in urls:
        logging.info(f"访问网址: {url}")
        log_display.insert(tk.END, f"访问网址: {url}\n")
        data = navigate_and_scrape(driver, url, max_pages, conn, cursor)
        all_scraped_data.extend(data)

    for item in all_scraped_data:
        logging.info(item)

    display_database_data()  # Display database data after scraping


# Scrape web page
def scrape_page(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    data = []
    rows = soup.select('tr.odd, tr.even')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) > 0:
            record = {
                'code': columns[1].text.strip(),
                'name': columns[2].text.strip(),
                'price': columns[4].text.strip(),
                'change_percent': columns[5].text.strip(),
                'change_amount': columns[6].text.strip(),
                'volume': columns[7].text.strip(),
                'turnover': columns[8].text.strip(),
                'amplitude': columns[9].text.strip(),
                'highest': columns[10].text.strip(),
                'lowest': columns[11].text.strip(),
                'open_price': columns[12].text.strip(),
                'close_price': columns[13].text.strip(),
                'volume_ratio': columns[14].text.strip(),
                'turnover_rate': columns[15].text.strip(),
                'pe_ratio': columns[16].text.strip(),
                'pb_ratio': columns[17].text.strip()
            }
            data.append(record)
    return data


# Navigate and scrape web page
def navigate_and_scrape(driver, url, max_pages, conn, cursor):
    driver.get(url)
    all_data = []
    page_count = 0

    while page_count < max_pages:
        try:
            time.sleep(5)
            data = scrape_page(driver)
            all_data.extend(data)
            logging.info(f"爬取到 {len(data)} 条数据，当前页数: {page_count + 1}")
            log_display.insert(tk.END, f"爬取到 {len(data)} 条数据，当前页数: {page_count + 1}\n")

            # Insert data into database
            for item in data:
                insert_into_database(conn, cursor, item)

            page_count += 1

            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.next'))
            )
            if 'disable' in next_button.get_attribute('class'):
                logging.info("没有更多的页可以翻了")
                log_display.insert(tk.END, "没有更多的页可以翻了\n")
                break
            else:
                next_button.click()
                time.sleep(3)
        except Exception as e:
            logging.error(f"发生异常: {e}")
            log_display.insert(tk.END, f"发生异常: {e}\n")
            break

    return all_data


# CRUD operations for selected item in the table
def delete_selected():
    selected_item = tree.selection()
    if selected_item:
        item_id = tree.item(selected_item)['values'][0]  # Assuming ID is the first column
        conn, cursor = init_database()
        delete_from_database(conn, cursor, item_id)
        conn.close()
        display_database_data()
        messagebox.showinfo("删除成功", f"已删除数据 ID: {item_id}")
    else:
        messagebox.showerror("删除错误", "请选择要删除的数据")


# GUI setup
root = tk.Tk()
root.title("东方财富网A股数据爬取")

# GUI elements
max_pages_label = ttk.Label(root, text="爬取页数:")
max_pages_label.pack(pady=10)

max_pages_entry = ttk.Entry(root)
max_pages_entry.pack()

start_button = ttk.Button(root, text="开始爬取", command=start_scraping)
start_button.pack(pady=20)

# Logging display
log_display = scrolledtext.ScrolledText(root, width=80, height=10)
log_display.pack(pady=10)

# Database data display in a table
tree = ttk.Treeview(root, columns=('ID', 'Code', 'Name', 'Price', 'Change %', 'Change Amount',
                                   'Volume', 'Turnover', 'Amplitude', 'Highest', 'Lowest',
                                   'Open Price', 'Close Price', 'Volume Ratio', 'Turnover Rate',
                                   'PE Ratio', 'PB Ratio'), show='headings', height=15)
tree.heading('ID', text='ID')
tree.heading('Code', text='Code')
tree.heading('Name', text='Name')
tree.heading('Price', text='Price')
tree.heading('Change %', text='Change %')
tree.heading('Change Amount', text='Change Amount')
tree.heading('Volume', text='Volume')
tree.heading('Turnover', text='Turnover')
tree.heading('Amplitude', text='Amplitude')
tree.heading('Highest', text='Highest')
tree.heading('Lowest', text='Lowest')
tree.heading('Open Price', text='Open Price')
tree.heading('Close Price', text='Close Price')
tree.heading('Volume Ratio', text='Volume Ratio')
tree.heading('Turnover Rate', text='Turnover Rate')
tree.heading('PE Ratio', text='PE Ratio')
tree.heading('PB Ratio', text='PB Ratio')
tree.pack(pady=20)

# Configure treeview columns
tree.column('ID', width=40, anchor=tk.CENTER)
tree.column('Code', width=90, anchor=tk.CENTER)
tree.column('Name', width=90, anchor=tk.CENTER)
tree.column('Price', width=70, anchor=tk.CENTER)
tree.column('Change %', width=90, anchor=tk.CENTER)
tree.column('Change Amount', width=70, anchor=tk.CENTER)
tree.column('Volume', width=90, anchor=tk.CENTER)
tree.column('Turnover', width=90, anchor=tk.CENTER)
tree.column('Amplitude', width=90, anchor=tk.CENTER)
tree.column('Highest', width=90, anchor=tk.CENTER)
tree.column('Lowest', width=90, anchor=tk.CENTER)
tree.column('Open Price', width=90, anchor=tk.CENTER)
tree.column('Close Price', width=90, anchor=tk.CENTER)
tree.column('Volume Ratio', width=90, anchor=tk.CENTER)
tree.column('Turnover Rate', width=90, anchor=tk.CENTER)
tree.column('PE Ratio', width=90, anchor=tk.CENTER)
tree.column('PB Ratio', width=90, anchor=tk.CENTER)

# Fetch initial database data and display in the table
display_database_data()

# Buttons for CRUD operations
crud_frame = ttk.Frame(root)
crud_frame.pack(pady=10)

delete_button = ttk.Button(crud_frame, text="删除选中", command=delete_selected)
delete_button.grid(row=0, column=0, padx=5)


def add_data():
    def add_to_database():
        new_data = {
            'code': code_entry.get(),
            'name': name_entry.get(),
            'price': price_entry.get(),
            'change_percent': change_percent_entry.get(),
            'change_amount': change_amount_entry.get(),
            'volume': volume_entry.get(),
            'turnover': turnover_entry.get(),
            'amplitude': amplitude_entry.get(),
            'highest': highest_entry.get(),
            'lowest': lowest_entry.get(),
            'open_price': open_price_entry.get(),
            'close_price': close_price_entry.get(),
            'volume_ratio': volume_ratio_entry.get(),
            'turnover_rate': turnover_rate_entry.get(),
            'pe_ratio': pe_ratio_entry.get(),
            'pb_ratio': pb_ratio_entry.get()
        }

        conn, cursor = init_database()
        insert_into_database(conn, cursor, new_data)
        conn.close()
        display_database_data()
        messagebox.showinfo("添加成功", "已成功添加新数据")
        add_window.destroy()

    # Create a new window for adding data
    add_window = tk.Toplevel(root)
    add_window.title("添加新数据")

    # GUI elements for data entry
    ttk.Label(add_window, text="Code:").grid(row=0, column=0, padx=5, pady=5)
    code_entry = ttk.Entry(add_window)
    code_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Name:").grid(row=1, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(add_window)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Price:").grid(row=2, column=0, padx=5, pady=5)
    price_entry = ttk.Entry(add_window)
    price_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Change Percent:").grid(row=3, column=0, padx=5, pady=5)
    change_percent_entry = ttk.Entry(add_window)
    change_percent_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Change Amount:").grid(row=4, column=0, padx=5, pady=5)
    change_amount_entry = ttk.Entry(add_window)
    change_amount_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Volume:").grid(row=5, column=0, padx=5, pady=5)
    volume_entry = ttk.Entry(add_window)
    volume_entry.grid(row=5, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Turnover:").grid(row=6, column=0, padx=5, pady=5)
    turnover_entry = ttk.Entry(add_window)
    turnover_entry.grid(row=6, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Amplitude:").grid(row=7, column=0, padx=5, pady=5)
    amplitude_entry = ttk.Entry(add_window)
    amplitude_entry.grid(row=7, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Highest:").grid(row=8, column=0, padx=5, pady=5)
    highest_entry = ttk.Entry(add_window)
    highest_entry.grid(row=8, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Lowest:").grid(row=9, column=0, padx=5, pady=5)
    lowest_entry = ttk.Entry(add_window)
    lowest_entry.grid(row=9, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Open Price:").grid(row=10, column=0, padx=5, pady=5)
    open_price_entry = ttk.Entry(add_window)
    open_price_entry.grid(row=10, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Close Price:").grid(row=11, column=0, padx=5, pady=5)
    close_price_entry = ttk.Entry(add_window)
    close_price_entry.grid(row=11, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Volume Ratio:").grid(row=12, column=0, padx=5, pady=5)
    volume_ratio_entry = ttk.Entry(add_window)
    volume_ratio_entry.grid(row=12, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="Turnover Rate:").grid(row=13, column=0, padx=5, pady=5)
    turnover_rate_entry = ttk.Entry(add_window)
    turnover_rate_entry.grid(row=13, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="PE Ratio:").grid(row=14, column=0, padx=5, pady=5)
    pe_ratio_entry = ttk.Entry(add_window)
    pe_ratio_entry.grid(row=14, column=1, padx=5, pady=5)

    ttk.Label(add_window, text="PB Ratio:").grid(row=15, column=0, padx=5, pady=5)
    pb_ratio_entry = ttk.Entry(add_window)
    pb_ratio_entry.grid(row=15, column=1, padx=5, pady=5)

    ttk.Button(add_window, text="确认添加", command=add_to_database).grid(row=16, column=0, columnspan=2, pady=10)


# Button to open add data window
add_button = ttk.Button(crud_frame, text="添加数据", command=add_data)
add_button.grid(row=0, column=1, padx=5)


def update_data(conn, cursor,  data):
    try:
        data['price'] = int(data['price'])
        update_query = """
        UPDATE scraped_data 
        SET code = %(code)s, 
            name = %(name)s, 
            price = %(price)s, 
            change_percent = %(change_percent)s, 
            change_amount = %(change_amount)s,
            volume = %(volume)s, 
            turnover = %(turnover)s, 
            amplitude = %(amplitude)s, 
            highest = %(highest)s, 
            lowest = %(lowest)s,
            open_price = %(open_price)s, 
            close_price = %(close_price)s, 
            volume_ratio = %(volume_ratio)s, 
            turnover_rate = %(turnover_rate)s,
            pe_ratio = %(pe_ratio)s, 
            pb_ratio = %(pb_ratio)s
        WHERE id = %(id)s
        """
        cursor.execute(update_query, data)
        conn.commit()
        logging.info(f"数据成功更新: ID {id}")
    except mysql.connector.Error as e:
        logging.error(f"更新数据错误: {e}")


def edit_selected():
    selected_item = tree.selection()
    if selected_item:
        def edit_in_database():
            updated_data = {
                'code': code_entry.get(),
                'name': name_entry.get(),
                'price': price_entry.get(),
                'change_percent': change_percent_entry.get(),
                'change_amount': change_amount_entry.get(),
                'volume': volume_entry.get(),
                'turnover': turnover_entry.get(),
                'amplitude': amplitude_entry.get(),
                'highest': highest_entry.get(),
                'lowest': lowest_entry.get(),
                'open_price': open_price_entry.get(),
                'close_price': close_price_entry.get(),
                'volume_ratio': volume_ratio_entry.get(),
                'turnover_rate': turnover_rate_entry.get(),
                'pe_ratio': pe_ratio_entry.get(),
                'pb_ratio': pb_ratio_entry.get(),
                'id':tree.item(selected_item)['values'][0]
            }
            conn, cursor = init_database()
            update_data(conn, cursor, updated_data)
            edit_window.destroy()
            display_database_data()  # 刷新数据显示

        # 创建编辑窗口
        edit_window = tk.Toplevel(root)
        edit_window.title("编辑数据")

        # 从数据库中获取当前选定的数据
        try:
            conn, cursor = init_database()
            select_query = "SELECT * FROM scraped_data WHERE id = %s"
            cursor.execute(select_query, (tree.item(selected_item)['values'][0],))
            current_data = cursor.fetchone()
            conn.close()

            if current_data:
                # 显示当前数据的编辑表单
                ttk.Label(edit_window, text="Code:").grid(row=0, column=0, padx=5, pady=5)
                code_entry = ttk.Entry(edit_window)
                code_entry.insert(0, current_data[1])  # 假设 'code' 是数据库中的第二列
                code_entry.grid(row=0, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Name:").grid(row=1, column=0, padx=5, pady=5)
                name_entry = ttk.Entry(edit_window)
                name_entry.insert(0, current_data[2])  # 假设 'name' 是数据库中的第三列
                name_entry.grid(row=1, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Price:").grid(row=2, column=0, padx=5, pady=5)
                price_entry = ttk.Entry(edit_window)
                price_entry.insert(0, current_data[3])  # 假设 'price' 是数据库中的第四列
                price_entry.grid(row=2, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Change Percent:").grid(row=3, column=0, padx=5, pady=5)
                change_percent_entry = ttk.Entry(edit_window)
                change_percent_entry.insert(0, current_data[4])  # 假设 'change_percent' 是数据库中的第五列
                change_percent_entry.grid(row=3, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Change Amount:").grid(row=4, column=0, padx=5, pady=5)
                change_amount_entry = ttk.Entry(edit_window)
                change_amount_entry.insert(0, current_data[5])  # 假设 'change_amount' 是数据库中的第六列
                change_amount_entry.grid(row=4, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Volume:").grid(row=5, column=0, padx=5, pady=5)
                volume_entry = ttk.Entry(edit_window)
                volume_entry.insert(0, current_data[6])  # 假设 'volume' 是数据库中的第七列
                volume_entry.grid(row=5, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Turnover:").grid(row=6, column=0, padx=5, pady=5)
                turnover_entry = ttk.Entry(edit_window)
                turnover_entry.insert(0, current_data[7])  # 假设 'turnover' 是数据库中的第八列
                turnover_entry.grid(row=6, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Amplitude:").grid(row=7, column=0, padx=5, pady=5)
                amplitude_entry = ttk.Entry(edit_window)
                amplitude_entry.insert(0, current_data[8])  # 假设 'amplitude' 是数据库中的第九列
                amplitude_entry.grid(row=7, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Highest:").grid(row=8, column=0, padx=5, pady=5)
                highest_entry = ttk.Entry(edit_window)
                highest_entry.insert(0, current_data[9])  # 假设 'highest' 是数据库中的第十列
                highest_entry.grid(row=8, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Lowest:").grid(row=9, column=0, padx=5, pady=5)
                lowest_entry = ttk.Entry(edit_window)
                lowest_entry.insert(0, current_data[10])  # 假设 'lowest' 是数据库中的第十一列
                lowest_entry.grid(row=9, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Open Price:").grid(row=10, column=0, padx=5, pady=5)
                open_price_entry = ttk.Entry(edit_window)
                open_price_entry.insert(0, current_data[11])  # 假设 'open_price' 是数据库中的第十二列
                open_price_entry.grid(row=10, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Close Price:").grid(row=11, column=0, padx=5, pady=5)
                close_price_entry = ttk.Entry(edit_window)
                close_price_entry.insert(0, current_data[12])  # 假设 'close_price' 是数据库中的第十三列
                close_price_entry.grid(row=11, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Volume Ratio:").grid(row=12, column=0, padx=5, pady=5)
                volume_ratio_entry = ttk.Entry(edit_window)
                volume_ratio_entry.insert(0, current_data[13])  # 假设 'volume_ratio' 是数据库中的第十四列
                volume_ratio_entry.grid(row=12, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="Turnover Rate:").grid(row=13, column=0, padx=5, pady=5)
                turnover_rate_entry = ttk.Entry(edit_window)
                turnover_rate_entry.insert(0, current_data[14])  # 假设 'turnover_rate' 是数据库中的第十五列
                turnover_rate_entry.grid(row=13, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="PE Ratio:").grid(row=14, column=0, padx=5, pady=5)
                pe_ratio_entry = ttk.Entry(edit_window)
                pe_ratio_entry.insert(0, current_data[15])  # 假设 'pe_ratio' 是数据库中的第十六列
                pe_ratio_entry.grid(row=14, column=1, padx=5, pady=5)

                ttk.Label(edit_window, text="PB Ratio:").grid(row=15, column=0, padx=5, pady=5)
                pb_ratio_entry = ttk.Entry(edit_window)
                pb_ratio_entry.insert(0, current_data[16])  # 假设 'pb_ratio' 是数据库中的第十七列
                pb_ratio_entry.grid(row=15, column=1, padx=5, pady=5)

                ttk.Button(edit_window, text="确认更新", command=edit_in_database).grid(row=16, column=0, columnspan=2,
                                                                                        pady=10)
            else:
                messagebox.showerror("数据错误", "未找到选定的数据")
                edit_window.destroy()  # 如果未找到数据，销毁编辑窗口

        except mysql.connector.Error as e:
            messagebox.showerror("数据库错误", f"无法获取数据: {str(e)}")

    else:
        messagebox.showerror("编辑错误", "请选择要编辑的数据")


# Button to open edit data window
edit_button = ttk.Button(crud_frame, text="编辑选中", command=edit_selected)
edit_button.grid(row=0, column=2, padx=5)


def search_data():
    keyword = search_entry.get().strip().lower()

    conn, cursor = init_database()
    select_query = "SELECT * FROM scraped_data WHERE LOWER(code) LIKE %s OR LOWER(name) LIKE %s"
    cursor.execute(select_query, (f"%{keyword}%", f"%{keyword}%"))
    search_results = cursor.fetchall()
    conn.close()

    # Clear existing table content
    for row in tree.get_children():
        tree.delete(row)

    # Insert search results into the table
    for row in search_results:
        tree.insert('', 'end', values=row)


# GUI elements for search functionality
search_frame = ttk.Frame(root)
search_frame.pack(pady=10)

search_label = ttk.Label(search_frame, text="搜索股票代码或名称:")
search_label.grid(row=0, column=0, padx=5)

search_entry = ttk.Entry(search_frame)
search_entry.grid(row=0, column=1, padx=5)

search_button = ttk.Button(search_frame, text="搜索", command=search_data)
search_button.grid(row=0, column=2, padx=5)

# Create Chrome WebDriver object
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

root.mainloop()
