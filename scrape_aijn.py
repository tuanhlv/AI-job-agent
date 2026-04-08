from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
import os

from pydantic import ValidationError

from job_record import JobRecord


class AIscraper:
    def __init__(self):
        self.url = os.getenv("AIJOBS_NET")
        self.scraped_jobs: list[JobRecord] = []

    async def get_tech_stack(self, session, job_url) -> list[str]:
        try:
            async with session.get(job_url) as response:
                html = await response.text()  # grab the raw text
            bs = BeautifulSoup(html, 'lxml')  # parse offline
            skills_section = bs.find('p')
            if skills_section:
                skills = skills_section.find_all('a')
                if skills:
                    skill_list = [skill.text.strip() for skill in skills]
                    # print(f"Successfully fetched {len(skill_list)} skills at {url}")
                    # print(skill_list)
                    return skill_list
        except Exception as e:
            print(f"Failed to fetch {job_url}: {e}")
        return []

    async def get_responsibility(self, session, job_url) -> list[str]:
        try:
            async with session.get(job_url) as response:
                html = await response.text()  # grab the raw text
            bs = BeautifulSoup(html, 'lxml')  # parse offline
            sections = bs.find_all('ul')
            if sections[0]:
                responsibility_section = sections[0]
                responsibilities = responsibility_section.find_all('li')
                if responsibilities:
                    responsibility_list = [task.text.strip() for task in responsibilities]
                    # print(f"Successfully fetched {len(responsibility_list)} benefits at {url}")
                    # print(responsibility_list)
                    return responsibility_list
        except Exception as e:
            print(f"Failed to fetch responsibilities at {job_url}: {e}")
        return []

    async def get_benefits(self, session, job_url) -> list[str]:
        try:
            async with session.get(job_url) as response:
                html = await response.text()  # grab the raw text
            bs = BeautifulSoup(html, 'lxml')  # parse offline
            sections = bs.find_all('ul')
            if sections[1]:
                benefit_section = sections[1]
                benefits = benefit_section.find_all('li')
                if benefits:
                    benefit_list = [perk.text.strip() for perk in benefits]
                    # print(f"Successfully fetched {len(benefit_list)} benefits at {url}")
                    # print(benefit_list)
                    return benefit_list
        except Exception as e:
            print(f"Failed to fetch benefits at {job_url}: {e}")
        return []

    async def scrape_jobs_aij(self) -> list[dict]:  # Fixed syntax: list[dict] instead of list(dict)
        validated_jobs = []

        # Open a single concurrent session for all requests
        headers = {"Accept-Encoding": "gzip, deflate"}  # force the server to send uncompressed data
        async with aiohttp.ClientSession(headers=headers) as session:

            # 1. Fetch the main page synchronously-style (but using our async session)
            async with session.get(self.url) as response:
                html = await response.text()

            bs = BeautifulSoup(html, 'lxml')
            job_cards = bs.find_all('li', class_=re.compile("d-flex justify-content"))

            # We will store the basic job info and the async tasks here temporarily
            job_info_list = []
            tech_stack_tasks = []
            responsibility_tasks = []
            benefit_tasks = []

            for card in job_cards:
                if not card:
                    continue

                tag = card.find('a', class_=re.compile("font-monospace fw-bold"))
                clean_title = ""
                job_url = None
                level = ""
                employment_type = ""
                location = ""

                if tag:
                    href = tag.get('href')
                    id = href.strip('/').split('/')[-1].split('-')[-1]
                    job_url = 'https://aijobs.net' + href
                    raw_title = tag.text.strip()
                    clean_title = raw_title.split('\n')[-1].strip()
                salary_element = card.find('span', class_=re.compile("text-bg-success"))
                salary = salary_element.text.strip() if salary_element else ""

                text_end = card.find('div', class_="text-end")
                if text_end:
                    level_element = text_end.find('span', class_=re.compile("text-bg-warning"))
                    level = level_element.text.strip() if level_element else ""
                    employment_type_element = text_end.find('span', class_=re.compile("text-bg-secondary"))
                    employment_type = employment_type_element.text.strip() if employment_type_element else ""
                    location_elements = text_end.find_all('div')
                    if len(location_elements) > 1:
                        location = location_elements[1].text.strip()

                # Save the basic info
                job_info_list.append({
                    'ID': id,
                    'Title': clean_title,
                    'Level': level,
                    'Employment_Type': employment_type,
                    'Location': location,
                    'Salary': salary
                })

                # Queue up the background tasks to fetch the tech stack concurrently
                if job_url:
                    tech_stack_tasks.append(self.get_tech_stack(session, job_url))
                    responsibility_tasks.append(self.get_responsibility(session, job_url))
                    benefit_tasks.append(self.get_benefits(session, job_url))
                else:
                    # If there's no URL, append a dummy task that returns an empty list
                    async def empty_list():
                        return []

                    tech_stack_tasks.append(empty_list())
                    responsibility_tasks.append(empty_list())
                    benefit_tasks.append(empty_list())

            print(
                f"Found {len(job_info_list)} jobs. Fetching tech stacks, responsibilities and benefits concurrently...")

            # ASYNC MAGIC: Run all requests at the exact same time
            all_tech_stacks = await asyncio.gather(*tech_stack_tasks)
            all_responsibilities = await asyncio.gather(*responsibility_tasks)
            all_benefits = await asyncio.gather(*benefit_tasks)

            # Convert tech stacks, responsibilities and benefits to strings
            # Then zip them back together with their matching job info
            for job, tech_stack, tasks, perks in zip(job_info_list, all_tech_stacks, all_responsibilities,
                                                     all_benefits):
                record = {
                    "id": job['ID'],
                    "title": job['Title'],
                    "level": job['Level'],
                    "employment_type": job['Employment_Type'],
                    "location": job['Location'],
                    "salary": job['Salary'],
                    "tech_stack": ", ".join(tech_stack),
                    "responsibilities": ", ".join(tasks),
                    "benefits": ", ".join(perks)
                }
                try:
                    validated_rec = JobRecord(**record)
                    validated_jobs.append(validated_rec)
                except ValidationError as e:
                    print(f"Skipping job ID {job.get('ID')} due to missing/invalid data: {e}")

        return validated_jobs

    def run(self):
        self.scraped_jobs = asyncio.run(self.scrape_jobs_aij())
