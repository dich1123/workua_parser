from requests import get
from bs4 import BeautifulSoup


class ParseWorkUa:
    def __init__(self, search_pattern, sal_from, sal_to, filename):
        self.search_pattern = search_pattern
        self.sal_from = self.get_fine_sallary(sal_from)
        self.sal_to = self.get_fine_sallary(sal_to)
        self.filename = filename

    @staticmethod
    def get_fine_sallary(info):
        variants = ['3000', '5000', '7000', '10000', '15000', '30000', '50000']
        ch = 2
        for i in range(len(variants)-1):
            if int(info) < int(variants[0]):
                return ch
            if int(variants[i]) < int(info) <= int(variants[i+1]):
                return ch + 1
            ch += 1
        return 8

    def get_page(self, page_number):
        link = f'https://www.work.ua/ru/jobs-kyiv-{self.search_pattern}/?advs=1' \
               f'&salaryfrom={self.sal_from}&salaryto={self.sal_to}&page={page_number}'
        response = get(link)
        html_soup = BeautifulSoup(response.content, 'html.parser')
        not_found = html_soup.findAll('title')
        if 'Ошибка 404' in str(not_found):
            print('Page not found 404')
            return None
        # print('LINK: ', link)
        return html_soup

    def get_numbers_of_pages(self, page):
        numbers = page.findAll('ul', {'class': 'pagination hidden-xs'})
        try:
            numbers = numbers[0].findChildren('li')
        except IndexError:
            return 1
        return int(str(numbers[-2]).split('>')[-3][:-3])

    def get_links_from_page(self, page):
        answ = []
        classes = page.findAll('h2', {'class': ''})
        # print(classes)
        for i in classes:
            info = i.findChildren('a', recursive=False)
            # print(info)
            if '"' in str(i):
                link = str(info).split('"')[1]
                # print('kekek', link)
                answ.append('https://www.work.ua' + link)
        return answ

    def get_info_via_link(self, link='https://www.work.ua/ru/jobs/3061923/'):
        response = get(link)
        html_soup = BeautifulSoup(response.content, 'html.parser')
        vacancy = html_soup.findAll('h1', {'class': 'add-top-sm', 'id': 'h1-name'})
        vacancy = vacancy[0].text

        payment = html_soup.findAll('b', {'class': 'text-black'})
        payment = payment[0].text

        company_name = html_soup.findAll('b')
        company_name = company_name[1].text

        place1 = html_soup.findAll('p', {'class': 'text-indent add-top-sm'})

        place = place1[0].text.strip().split('\n')[0]
        requirements = place1[1].text.strip()

        return {'vac': vacancy, 'pay': payment, 'company': company_name,
                'place': place, 'req': requirements, 'link': link}

    def parse_all_and_save(self):
        try:
            with open(self.filename, 'a') as file:
                pass
        except FileNotFoundError:
            with open(self.filename, 'w') as file:
                pass

        page1 = self.get_page(1)
        max_pages = self.get_numbers_of_pages(page1)
        with open(self.filename, 'a') as file:
            for i in range(0, max_pages-30):
                links = self.get_links_from_page(page1)
                for link in links:
                    print(f'-> working page: {i+1}')
                    info = self.get_info_via_link(link)
                    write_info = f'Vacancy:{info["vac"]}\nPayment:{info["pay"]}\nCompany:{info["company"]}\n' \
                                 f'Place:{info["place"]}\nLink:{info["link"]}\n\n'
                    file.write(write_info)
                page1 = self.get_page(i+1)


a = ParseWorkUa('бухгалтер', 10000, 30000, 'save.txt')
a.parse_all_and_save()
# b = a.get_page(1)
# print(b.text)
# c = a.get_numbers_of_page(b)
# d = a.get_links_from_page(b)
# print(a.get_info_via_link('https://www.work.ua/ru/jobs/2272210/'))
# print(d)
