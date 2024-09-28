from bs4 import BeautifulSoup
from dataclasses import dataclass
import time


@dataclass
class Resume:
    title: str
    name: str
    years: str
    location: str
    skills: list


def parse_single_resume(resume_html, driver):
    soup = BeautifulSoup(resume_html, "html.parser")
    title_tag = soup.select_one("h2 a")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"
    name_tag = soup.select_one("p.mt-xs .strong-600")
    name = name_tag.get_text(strip=True) if name_tag else "N/A"
    years_tag = soup.select_one("p.mt-xs span:nth-of-type(2)")
    years = years_tag.get_text(strip=True).replace("\xa0", " ") if years_tag else "N/A"
    location_tag = soup.select_one("p.mt-xs span:nth-of-type(3)")
    location = location_tag.get_text(strip=True) if location_tag else "N/A"

    resume = Resume(title=title, name=name, years=years, location=location, skills=[])

    detail_url_tag = soup.select_one('h2.mt-0 a[tabindex="-1"]')
    if detail_url_tag:
        detail_url = "https://www.work.ua" + detail_url_tag["href"]
        resume.skills = get_resume_skills(detail_url, driver)
    return resume


def get_num_pages(soup):
    pagination = soup.select_one("ul.pagination")
    if pagination is None:
        return 1
    return int(pagination.select("li")[-2].get_text(strip=True))


def get_single_page_resume(page_url, driver):
    driver.get(page_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    resume_cards = soup.select("div.card.card-hover")
    resumes = [parse_single_resume(str(card), driver) for card in resume_cards]

    return resumes


def get_resume_skills(detail_url, driver):
    driver.get(detail_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    skills_list = []
    skills_items = soup.select(
        "ul.list-unstyled.my-0.flex.flex-wrap li span.label.label-skill span.ellipsis"
    )
    for skill in skills_items:
        skill_name = skill.get_text(strip=True)
        skills_list.append(skill_name)

    return skills_list


def get_all_resumes(driver):
    base_url = "https://www.work.ua/resumes-remote-python+developer/"
    driver.get(base_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    num_pages = get_num_pages(soup)
    all_resumes = []
    all_resumes.extend(get_single_page_resume(base_url, driver))

    for page_num in range(2, num_pages + 1):
        page_url = f"{base_url}? page={page_num}"
        all_resumes.extend(get_single_page_resume(page_url, driver))
    return all_resumes
