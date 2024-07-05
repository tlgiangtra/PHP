import os
import time
import threading
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Đường dẫn tới ChromeDriver của bạn
chrome_driver_path = 'C:\\webdriver\\chromedriver.exe'

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    # Thêm các user-agent khác vào đây
]

# Hàm để xóa một tài khoản khỏi accounts.txt
def remove_account_entry(accounts_file, user):
    temp_file = accounts_file + '.tmp'
    with open(accounts_file, 'r', encoding='utf-8') as f, open(temp_file, 'w', encoding='utf-8') as temp:
        for line in f:
            if not line.startswith(user):
                temp.write(line)
    os.remove(accounts_file)
    os.rename(temp_file, accounts_file)

# Hàm tạo tài khoản
def create_account(user, password, accounts_file, profile_dir):
    options = uc.ChromeOptions()

    # Thêm các tùy chọn Chrome khác
    options.add_argument("--lang=vi-VN")
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-geolocation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Đặt kích thước cửa sổ
    options.add_argument("--window-size=450,800")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--incognito")  # Thêm tùy chọn ẩn danh
    driver = uc.Chrome(options=options)

    try:
        driver.set_window_size(450, 800)  # Đặt kích thước cửa sổ sau khi khởi động trình duyệt
        driver.set_window_position(0, 0)  # Đặt vị trí cửa sổ để tránh trường hợp bị đặt lệch ra ngoài màn hình

        driver.get('https://account.riotgames.com')
        time.sleep(random.uniform(1, 3))  # Thêm độ trễ ngẫu nhiên

        # Click nút lưu (nếu có)
        try:
            save_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "osano-cm-save")]')))
            save_button.click()
        except:
            pass

        # Đợi các phần tử biến mất (nếu có)
        try:
            WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'osano-cm-dialog')))
        except:
            pass

        username_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'username')))
        username_input.send_keys(user)

        password_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'password')))
        password_input.send_keys(password)

        signup_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/main/div/form/div/div/div[2]/button')))
        signup_button.click()

        time.sleep(30)

        riot_id_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@data-testid="riot-id__riotId"]')))
        riot_id_input.send_keys(user)

        tagline_input = driver.find_element(By.XPATH, '//input[@data-testid="riot-id__tagline"]')
        tagline_input.send_keys(user[-5:])

        save_button = driver.find_element(By.XPATH, '//button[@data-testid="riot-id__save-btn"]')
        save_button.click()

        time.sleep(10)  # Đợi 1 phút trước khi khởi động lại tab

        print(f"Veri {user} thành công!")

        with open('veriacc.txt', 'a') as f:
            f.write(f"{user}|{password}|{user}|{user[-5:]}\n")

        remove_account_entry(accounts_file, user)

    except Exception as e:
        print(f"Lỗi xảy ra với {user}: {str(e)}")
    finally:
        driver.quit()

# Hàm xử lý từng tài khoản trong một luồng riêng
def process_account(account_line, accounts_file, profile_dir):
    user, password = account_line.strip().split('=')
    create_account(user, password, accounts_file, profile_dir)
    time.sleep(5)  # Đợi 1 phút trước khi khởi động lại tab

# Hàm chính
def main():
    accounts_file = '2.txt'
    with open(accounts_file, 'r', encoding='utf-8') as f:
        accounts = f.readlines()

    num_threads = 1  # Tăng số lượng luồng lên
    threads = []

    for i, account_line in enumerate(accounts):
        profile_dir = f'C:\\webdriver\\profile_{i}'  # Tạo một profile mới cho mỗi phiên
        while len(threads) >= num_threads:
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)
                    break
            time.sleep(10)
        t = threading.Thread(target=process_account, args=(account_line, accounts_file, profile_dir))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
