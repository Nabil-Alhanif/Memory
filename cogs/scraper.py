import os
import random
import re
import requests
import shutil

from bs4 import BeautifulSoup
from module.pdf import PDF
from PIL import Image
from time import time
from urllib.parse import urlparse

import discord
from discord.ext import commands

def extractImgFromHTML(image_list):
    for i in range(len(image_list)):
        image_list[i] = re.sub("'", '"', str(image_list[i]))
        image_list[i] = re.findall(r'img.*?src="(.*?)"', str(image_list[i]))

    ret = [item for item in image_list if item != []]
        
    return ret

class PageData:
    def __init__(self, author, url):
        self.author = author
        self.url = url

    def scrape(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.find("title")
        
        subject = re.findall(r'>(.*?) [|]', str(title))
        subject = " | ".join(subject)
        
        self.subject = subject

        diff = re.findall(r'[(](.*?)[)]', str(title))
        diff = " | ".join(diff)

        cur_time = str(time())

        self.name = subject + " - " + diff
        self.question_file = str(self.author) + " - Questions - " + cur_time + " - " + self.name
        self.solution_file = str(self.author) + " - Solutions - " + cur_time + " - " + self.name

        questions = soup.find_all("div", class_="question-problem")
        self.questions = extractImgFromHTML(questions)

        solutions = soup.find_all("script")
        self.solutions = extractImgFromHTML(solutions)

class Scraper(commands.Cog, name='Scraper'):
    def __init__(self, bot):
        self.bot = bot

    def processUrlDifficulty(self, url: str):
        urls = {}
        
        if len(re.findall(r'/easy', url)): # This is an easy question
            urls["easy"] = url
            urls["medium"] = re.sub('/easy', '/medium', url)
            urls["hard"] = re.sub('/easy', '/hard', url)
        elif len(re.findall(r'/medium', url)): # This is a medium question
            urls["easy"] = re.sub('/medium', '/easy', url)
            urls["medium"] = url
            urls["hard"] = re.sub('/medium', '/hard', url)
        elif len(re.findall(r'/hard', url)): # This is a hard question
            urls["easy"] = re.sub('/hard', '/easy', url)
            urls["medium"] = re.sub('/hard', '/medium', url)
            urls["hard"] = url

        return urls

    def extractImgToPdf(self, image_list, pdf_name: str, width = 210, height = 297):
        print("Now processing: " + pdf_name)
        image_name = []

        for i in range(len(image_list)):
            for j in range(len(image_list[i])):
                print(image_list[i][j])
                response = requests.get(image_list[i][j], stream=True)
                name = str(pdf_name) + str(i) + str(j) + ".png"
                with open(name, "wb") as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                    image_name.append(name)

        pdf = PDF()
        for image in image_name:
            pdf.add_page()
            im = Image.open(image)
            w, h = im.size

            # Resize both, just in case :wink
            if (w > width):
                h = int(h * (width / w))
                w = width
                
            if (h > height):
                w = int(w * (height / h))
                h = height

            pdf.image(image, x = 0, y = 0, w = w, h = h)
            im.close()

            os.remove(image)

        pdf.output(pdf_name + ".pdf")

    def uri_validator(self, uri):
        try:
            result = urlparse(uri)
            return all([result.scheme, result.netloc])
        except:
            return False

    @commands.command(name="dsme", help="Scrape a question topic from savemyexams.co.uk")
    async def dsme(self, ctx, url: str):
        # Validate the url
        if not self.uri_validator(url):
            await ctx.send(f'Hey {ctx.author.mention}, the url you send is not valid! Please check it again!')
            return

        # Validate that the link is really of savemyexams.co.uk
        if not url.startswith("https://www.savemyexams.co.uk"):
            await ctx.send(f'Hey {ctx.author.mention}, the link you send is not one of savemyexams.co.uk! Please check it again!')

        await ctx.send(f'Hey {ctx.author.mention}, I\'m processing your request! This process will usually take less than 1 minute depending on the amount of requests I\'m currently processing!')
        
        # Scrape the webpage
        data = PageData(ctx.author, url)
        data.scrape()
        
        self.extractImgToPdf(data.questions, data.question_file)
        self.extractImgToPdf(data.solutions, data.solution_file)

        outputs = [
            discord.File(data.question_file + ".pdf", "Questions - " + data.name + ".pdf"),
            discord.File(data.solution_file + ".pdf", "Solutions - " + data.name + ".pdf"),
        ]

        await ctx.send(f'Hey {ctx.author.mention}, here are the files you requested!', files = outputs)

        # Cleanup
        os.remove(data.question_file + ".pdf")
        os.remove(data.solution_file + ".pdf")

    # Not gonna lie, this whole function feels like a frickin hacky solution
    @commands.command(name="dsmes", help="Scrape a question topic from savemyexams.co.uk")
    async def dsmes(self, ctx, url: str, easy_question_count: int = 5, medium_question_count: int = 3, hard_question_count: int = 2):
        # Validate the url
        if not self.uri_validator(url):
            await ctx.send(f'Hey {ctx.author.mention}, the url you send is not valid! Please check it again!')
            return

        # Validate that the link is really of savemyexams.co.uk
        if not url.startswith("https://www.savemyexams.co.uk"):
            await ctx.send(f'Hey {ctx.author.mention}, the link you send is not one of savemyexams.co.uk! Please check it again!')

        await ctx.send(f'Hey {ctx.author.mention}, I\'m processing your request! This process will usually take less than 1 minute depending on the amount of requests I\'m currently processing!')

        urls = self.processUrlDifficulty(url)

        # Scrape the webpage
        easy_rawdata = PageData(ctx.author, urls["easy"])
        easy_rawdata.scrape()
        print(easy_rawdata.questions, end="\n")
        print(easy_rawdata.solutions, end="\n\n")

        medium_rawdata = PageData(ctx.author, urls["medium"])
        medium_rawdata.scrape()
        print(medium_rawdata.questions, end="\n")
        print(medium_rawdata.solutions, end="\n\n")

        hard_rawdata = PageData(ctx.author, urls["hard"])
        hard_rawdata.scrape()
        print(hard_rawdata.questions, end="\n")
        print(hard_rawdata.solutions, end="\n\n")

        # Get important variable
        subject = str(easy_rawdata.subject)

        # Make sure the question count is at most the same as amount of question available
        easy_question_count = min(easy_question_count, len(easy_rawdata.questions))
        medium_question_count = min(medium_question_count, len(medium_rawdata.questions))
        hard_question_count = min(hard_question_count, len(hard_rawdata.questions))

        easy_data = []
        medium_data = []
        hard_data = []

        # We can use easy_rawdata.questions here,
        # because the amount of question and solution should be the same
        for i in range(len(easy_rawdata.questions)):
            easy_data.append([easy_rawdata.questions[i], easy_rawdata.solutions[i]])

        for i in range(len(medium_rawdata.questions)):
            medium_data.append([medium_rawdata.questions[i], medium_rawdata.solutions[i]])

        for i in range(len(hard_rawdata.questions)):
            hard_data.append([hard_rawdata.questions[i], hard_rawdata.solutions[i]])

        easy_selection = random.sample(easy_data, easy_question_count)
        medium_selection = random.sample(medium_data, medium_question_count)
        hard_selection = random.sample(hard_data, hard_question_count)

        questions = []
        solutions = []
        
        for i in [easy_selection, medium_selection, hard_selection]:
            for j in i:
                questions.append(j[0])
                solutions.append(j[1])

        cur_time = str(time())

        question_file = str(ctx.author) + " - Questions - " + cur_time + subject
        solution_file = str(ctx.author) + " - Solutions - " + cur_time + subject

        self.extractImgToPdf(questions, question_file)
        self.extractImgToPdf(solutions, solution_file)

        outputs = [
            discord.File(question_file + ".pdf", "Questions - " + subject + ".pdf"),
            discord.File(solution_file + ".pdf", "Solutions - " + subject + ".pdf"),
        ]

        await ctx.send(f'Hey {ctx.author.mention}, here are the files you requested!', files = outputs)

        # Cleanup
        os.remove(question_file + ".pdf")
        os.remove(solution_file + ".pdf")