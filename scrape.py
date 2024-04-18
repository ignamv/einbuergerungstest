"""Scrape website and store results in database"""

from itertools import count
import selenium.webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from db import conn, create_table

# import sys

# driverpath = "/home/ignacio/packages/geckodriver"
# if driverpath not in sys.path:
# sys.path.append(driverpath)

MAXIMUM_GENERAL_QUESTION_INDEX = 300


def iterate_select_options(select):
    """Click on each option in select and yield option text"""
    # Can't reuse the actual option reference because there might be navigation between iterations
    for ii, _ in enumerate(select().options):
        option = select().options[ii]
        text = option.text
        option.click()
        yield text


def scrape_all(driver):
    """Yield questions and answers for all Bundesländer

    Each element is bundesland,image_bytes,answers,correct_answer_index
    `correct_answer_index` is 0-based
    """
    driver.get("https://oet.bamf.de/ords/oetut/f?p=514:1:0")
    # Need to refresh reference to element because of navigation between iterations
    select = lambda: Select(driver.find_element(By.ID, "P1_BUL_ID"))
    for bundesland_index, bundesland in enumerate(iterate_select_options(select)):
        # Go to the questions
        driver.find_element(By.XPATH, '//input[@value="Zum Fragenkatalog"]').click()
        # The general questions are the same for all Bundesländer,
        # only scrape them for the first Bundesland
        scrape_general_questions = bundesland_index == 0
        for question in scrape_bundesland(driver, scrape_general_questions):
            general_question, image_bytes, answers, correct_answer_index = question
            effective_bundesland = bundesland if not general_question else None
            yield effective_bundesland, image_bytes, answers, correct_answer_index
        driver.find_element(By.XPATH, '//input[@value="zur Startseite"]').click()


def scrape_bundesland(driver, scrape_general_questions):
    """Yield all questions for a bundesland

    Each question is general_question, image_bytes, answers, correct_answer_index

    general_question is True if the question is not Bundesland-specific
    """
    # Skip the general questions if necessary
    first_question_index = (
        1 if scrape_general_questions else MAXIMUM_GENERAL_QUESTION_INDEX + 1
    )
    Select(driver.find_element(By.ID, "P30_ROWNUM")).select_by_visible_text(
        str(first_question_index)
    )

    for question_index in count(first_question_index):
        image_bytes, answers, correct_answer_index = scrape_question(driver)
        general_question = question_index <= MAXIMUM_GENERAL_QUESTION_INDEX
        yield general_question, image_bytes, answers, correct_answer_index
        try:
            driver.find_element(By.NAME, "GET_NEXT_ID").click()
        except NoSuchElementException:
            # Last question
            break


def scrape_question(driver):
    """Return question image, answers and correct answer index"""
    # Fetch image
    img = driver.find_element(By.XPATH, "//img[contains(@src, 'APPLICATION_PROCESS')]")
    image_bytes = img.screenshot_as_png
    # Click first answer so we can look at the CSS to see which answer is correct
    driver.find_element(By.XPATH, "//input[@type='radio']").click()

    table = driver.find_element(By.XPATH, "//table[@class='t3borderless']")
    rows = table.find_elements(By.TAG_NAME, "tr")

    answers = []
    for ii, row in enumerate(rows):
        correct = (
            row.find_element(By.XPATH, "td[@headers='CHECKBOX']").get_attribute("style")
            == "background-color: green;"
        )
        if correct:
            correct_answer_index = ii
        answer = row.find_element(By.XPATH, "td[@headers='ANTWORT']").text
        answers.append(answer)
    return image_bytes, answers, correct_answer_index


def scrape_to_db():
    """Create driver and scrape questions to database"""
    driver = selenium.webdriver.Firefox()
    for question in scrape_all(driver):
        effective_bundesland, image_bytes, answers, correct_answer_index = question
        conn.execute(
            "INSERT INTO questions "
            "(bundesland,question_png_bytes,answer0,answer1,answer2,answer3,correct_answer_index) "
            "VALUES (?,?,?,?,?,?,?)",
            (effective_bundesland, image_bytes)
            + tuple(answers)
            + (correct_answer_index,),
        )
        conn.commit()


if __name__ == "__main__":
    create_table()
    scrape_to_db()
