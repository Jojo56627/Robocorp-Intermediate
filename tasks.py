from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def minimal_task():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    #get_orders_file()
    #open_order_page()
    #giv_up_constitutional_rights()
    #fill_form_with_csv_data()
    zip_it_up()

def open_order_page():
    """Opens the order pagew and accepts the loose of constitutional rigths"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def giv_up_constitutional_rights():
    page = browser.page()
    page.click(".btn-dark")

def get_orders_file():
    """Downloads the data-csv-file from the remote address"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fill_form_with_csv_data():
    """Reads CSV File"""
    lib = Tables()
    csv = lib.read_table_from_csv("orders.csv", header=True)

    for row in csv:
        place_order(row)
        order_another()

def place_order(order):
    """Places the the supplied order"""    
    page = browser.page()

    page.select_option("#head", order["Head"])
    page.fill("input[type=number]", str(order["Legs"]))
    page.click("#id-body-" + str(order["Body"]))
    page.fill("#address", order["Address"])

    page.click('#order')

    while not assert_order_sent():
        continue

    store_receipt_as_pdf(order["Order number"])

def assert_order_sent():

    page = browser.page()
    order_sent = False

    try:
        page.wait_for_selector(selector='.alert-danger', timeout=1500)
        page.locator('#order').click()
        try:
            page.wait_for_selector(selector='.alert-success', timeout=1500)
            order_sent = True
        except:
            None

    except:
        try:
            page.wait_for_selector(selector='.alert-success', timeout=1500)
            order_sent = True
        except TimeoutError:
            None

    return order_sent

def order_another():
    page = browser.page()

    page.click("#order-another")
    giv_up_constitutional_rights()

def store_receipt_as_pdf(order_number):
    page = browser.page()

    receipt = page.locator("#receipt").inner_html()

    receipt_path = "output/receipts/receipt_" + str(order_number) + ".pdf"
    screenshot_path = take_robot_screenshot(order_number)

    pdf = PDF()
    pdf.html_to_pdf(receipt, receipt_path)
    pdf.add_files_to_pdf(files=[screenshot_path], target_document=receipt_path, append=True)


def take_robot_screenshot(order_number):

    screenshot_path = f'./output/created-robots/{order_number}-robot.png'
    page = browser.page()
    page.locator('#robot-preview-image').screenshot(path=screenshot_path)
    
    return screenshot_path

def zip_it_up():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip')