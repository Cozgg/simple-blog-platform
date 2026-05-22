import os
import time

import pytest
from selenium.webdriver.common.by import By

from blogapp.test.pages.LoginPage import LoginPage
from blogapp.test.pages.ProfilePage import ProfilePage
from blogapp.test.test_base import driver
from blogapp.test.test_base import post_factory


def save_step_screenshot(driver, test_name, step):
    folder = f"screenshots/{test_name}"

    os.makedirs(folder, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    path = f"{folder}/{step}_{timestamp}.png"

    driver.save_screenshot(path)


def login_and_open_profile(driver, user_id, username="canhhuynh"):
    login = LoginPage(driver)

    login.open_page()
    login.login(username, "123456")

    time.sleep(1)

    profile = ProfilePage(driver)
    profile.open_page(user_id=user_id)

    time.sleep(1)

    return profile


def get_first_post(profile):
    return profile.finds(
        By.CSS_SELECTOR,
        "#post-list-container > div"
    )[0]


def get_post_buttons(post):
    buttons = post.find_elements(By.TAG_NAME, "button")

    return {
        "pin": buttons[0],
        "lock": buttons[1]
    }


def assert_no_action_button(posts, action_name):
    for post in posts:
        buttons = post.find_elements(
            By.CSS_SELECTOR,
            f"button[onclick^='{action_name}']"
        )

        assert len(buttons) == 0


@pytest.mark.selenium
class TestPinPost:

    def test_pinned_post_success(self, driver, post_factory):
        p = post_factory(username="canhhuynh")

        profile = login_and_open_profile(
            driver,
            user_id=3
        )

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)


        buttons["pin"].click()

        time.sleep(2)

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)

        badge = first_post.find_elements( By.ID, "pinned" )[0]

        delete_btn = first_post.find_elements(
            By.CSS_SELECTOR,
            "button[onclick^='deletePost']"
        )


        assert buttons["pin"].text == "Bỏ ghim"
        assert badge.text == "Đã ghim"
        assert len(delete_btn) == 0

    def test_unpinned_post_success(self, driver, post_factory):
        p = post_factory(
            username="canhhuynh",
            is_pinned=True
        )

        profile = login_and_open_profile(
            driver,
            user_id=3
        )

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)


        buttons["pin"].click()

        time.sleep(2)

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)

        delete_btn = first_post.find_element(
            By.CSS_SELECTOR,
            "button[onclick^='deletePost']"
        )


        assert buttons["pin"].text == "Ghim bài"

        assert not first_post.find_elements(
            By.ID,
            f"pinned-post-{p.id}"
        )

        assert delete_btn.text == "Xóa"

    def test_pinned_other_post(self, driver, post_factory):

        post_factory(username="ngocson", is_pinned=True)
        post_factory(username="ngocson", is_locked=True)
        post_factory(username="ngocson", is_pinned=True)
        post_factory(username="ngocson", is_locked=True)

        profile = login_and_open_profile(
            driver,
            user_id=2
        )


        while True:

            driver.execute_script(
                "window.scrollTo(0, 5000)"
            )

            posts = profile.finds(
                By.CSS_SELECTOR,
                "#post-list-container > div"
            )

            assert_no_action_button(
                posts,
                "pinPost"
            )

            save_step_screenshot(
                driver,
                "test_pinned_other_post",
                "02_checked_page"
            )

            next_page_li = profile.find(
                By.ID,
                "next-page-btn"
            )

            if "disabled" in next_page_li.get_attribute("class"):
                break

            next_link = next_page_li.find_element(
                By.TAG_NAME,
                "a"
            )

            if next_link:
                next_link.click()

            time.sleep(1)


@pytest.mark.selenium
class TestLockPost:

    def test_lock_post_success(self, driver, post_factory):
        p = post_factory(username="canhhuynh")

        profile = login_and_open_profile(
            driver,
            user_id=3
        )

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)

        save_step_screenshot(
            driver,
            "test_lock_post_success",
            "02_before_lock"
        )

        buttons["lock"].click()

        time.sleep(2)

        save_step_screenshot(
            driver,
            "test_lock_post_success",
            "03_after_lock_click"
        )

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)

        badge = first_post.find_elements( By.ID, "locked" )[0]

        delete_btn = first_post.find_elements(
            By.CSS_SELECTOR,
            "button[onclick^='deletePost']"
        )


        assert buttons["lock"].text == "Mở khóa"
        assert badge.text == "Đã khóa"
        assert len(delete_btn) == 0

    def test_unlock_post_success(self, driver, post_factory):
        p = post_factory(
            username="canhhuynh",
            is_locked=True
        )

        profile = login_and_open_profile(
            driver,
            user_id=3
        )


        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)

        save_step_screenshot(
            driver,
            "test_unlock_post_success",
            "02_before_unlock"
        )

        buttons["lock"].click()

        time.sleep(2)

        save_step_screenshot(
            driver,
            "test_unlock_post_success",
            "03_after_unlock_click"
        )

        first_post = get_first_post(profile)

        buttons = get_post_buttons(first_post)

        delete_btn = first_post.find_element(
            By.CSS_SELECTOR,
            "button[onclick^='deletePost']"
        )


        assert buttons["lock"].text == "Khóa bài"

        assert not first_post.find_elements(
            By.ID,
            f"locked-post-{p.id}"
        )

        assert delete_btn.text == "Xóa"

    def test_locked_other_post(self, driver, post_factory):

        post_factory(username="ngocson", is_locked=True)
        post_factory(username="ngocson", is_pinned=True)
        post_factory(username="ngocson", is_locked=True)
        post_factory(username="ngocson", is_pinned=True)

        profile = login_and_open_profile(
            driver,
            user_id=2
        )


        while True:

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)"
            )

            posts = profile.finds(
                By.CSS_SELECTOR,
                "#post-list-container > div"
            )

            assert_no_action_button(
                posts,
                "lockPost"
            )

            save_step_screenshot(
                driver,
                "test_locked_other_post",
                "02_checked_page"
            )

            next_page_li = profile.find(
                By.ID,
                "next-page-btn"
            )

            if "disabled" in next_page_li.get_attribute("class"):
                break

            next_link = next_page_li.find_element(
                By.TAG_NAME,
                "a"
            )

            next_link.click()

            time.sleep(1)


@pytest.mark.selenium
def test_pinned_and_locked_post(driver, post_factory):

    p = post_factory(username="canhhuynh")

    profile = login_and_open_profile(
        driver,
        user_id=3
    )


    first_post = get_first_post(profile)

    buttons = get_post_buttons(first_post)

    buttons["pin"].click()

    time.sleep(2)

    save_step_screenshot(
        driver,
        "test_pinned_and_locked_post",
        "02_after_pin"
    )

    first_post = get_first_post(profile)

    buttons = get_post_buttons(first_post)

    buttons["lock"].click()

    time.sleep(2)

    save_step_screenshot(
        driver,
        "test_pinned_and_locked_post",
        "03_after_lock"
    )

    first_post = get_first_post(profile)

    buttons = get_post_buttons(first_post)

    pinned_badge = first_post.find_element(
        By.ID,
        f"pinned"
    )

    locked_badge = first_post.find_element(
        By.ID,
        f"locked"
    )


    assert buttons["pin"].text == "Bỏ ghim"
    assert pinned_badge.text == "Đã ghim"

    assert buttons["lock"].text == "Mở khóa"
    assert locked_badge.text == "Đã khóa"