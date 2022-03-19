import os
import re
import requests
import shutil

from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image
from urllib.parse import urlparse

import discord
from discord.ext import commands

class Scraper(commands.Cog, name='Scraper'):
    def __init__(self, bot):
        self.bot = bot

    def extractImgToPdf(self, image_list, pdf_name: str, width = 210, height = 297):
        image_name = []

        for i in range(len(image_list)):
            image_list[i] = re.sub("'", '"', str(image_list[i]))
            image_list[i] = re.findall(r'img.*?src="(.*?)"', str(image_list[i]))

            for j in range(len(image_list[i])):
                print(image_list[i][j])
                response = requests.get(image_list[i][j], stream=True)
                name = str(pdf_name) + str(i) + str(j) + ".png"
                with open(name, "wb") as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                    image_name.append(name)

        pdf = FPDF()
        for image in image_name:
            pdf.add_page()
            im = Image.open(image)
            w, h = im.size

            if (w > h):
                if (w > width):
                    h = int(h * (width / w))
                    w = width
            else:
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

        # Scrape the webpage
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.find("title")
        
        subject = re.findall(r'>(.*?) [|]', str(title))
        subject = " | ".join(subject)

        diff = re.findall(r'[(](.*?)[)]', str(title))
        diff = " | ".join(diff)

        name = subject + " - " + diff
        question_file = str(ctx.author) + " - Questions - " + name
        solution_file = str(ctx.author) + " - Solutions - " + name

        questions = soup.find_all("div", class_="question-problem")
        self.extractImgToPdf(questions, question_file)

        solutions = soup.find_all("script")
        self.extractImgToPdf(solutions, solution_file)

        outputs = [
            discord.File(question_file + ".pdf", "Questions - " + name + ".pdf"),
            discord.File(solution_file + ".pdf", "Solutions - " + name + ".pdf"),
        ]

        await ctx.send(f'Hey {ctx.author.mention}, here are the files you requested!', files = outputs)

        # Cleanup
        os.remove(question_file + ".pdf")
        os.remove(solution_file + ".pdf")
