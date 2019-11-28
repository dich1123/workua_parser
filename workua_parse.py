from requests import get
from bs4 import BeautifulSoup


class ParseWorkUa:
    def __init__(self, search_pattern, sal_from, sal_to, filename):
        '''Class do basic parse of workua in Kiev with your search request and fixed salary

        :param search_pattern: for example "junior python" or "бухгалтер"
        :param sal_from: your required minimum salary
        :param sal_to: your required maximum salary
        :param filename: output file, where will be saved your data
        '''
        self.search_pattern = search_pattern
        self.sal_from = self.get_fine_sallary(sal_from)
        self.sal_to = self.get_fine_sallary(sal_to)
        self.filename = filename

    @staticmethod
    def get_fine_sallary(info):
        '''
        Change your salary to workua variant
        :param info: for example 10000 (int) it's in UAH
        :return: valid salary for workua understanding
        '''
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
        '''
        :param page_number: for example 1 (int) WARNING! Don't use it with big int if you're not sure
        :return: bs4 page
        '''
        link = f'https://www.work.ua/ru/jobs-kyiv-{self.search_pattern}/?advs=1' \
               f'&salaryfrom={self.sal_from}&salaryto={self.sal_to}&page={page_number}'
        response = get(link)
        html_soup = BeautifulSoup(response.content, 'html.parser')
        not_found = html_soup.findAll('title')
        if 'Ошибка 404' in str(not_found):
            print('Page not found 404')
            return None
        return html_soup

    def get_numbers_of_pages(self, page):
        '''
        Give you max value of page number for current search request
        :param page: bs4 page (with current search, for example 1st page)
        :return: value with max page number (int)
        '''
        numbers = page.findAll('ul', {'class': 'pagination hidden-xs'})
        try:
            numbers = numbers[0].findChildren('li')
        except IndexError:
            return 1
        return int(str(numbers[-2]).split('>')[-3][:-3])

    def get_links_from_page(self, page):
        '''
        Take all links to vacancies from page
        :param page: page (bs4)
        :return: list with links
        '''
        answ = []
        classes = page.findAll('h2', {'class': ''})
        for i in classes:
            info = i.findChildren('a', recursive=False)
            if '"' in str(i):
                link = str(info).split('"')[1]
                answ.append('https://www.work.ua' + link)
        return answ

    def get_info_via_link(self, link='https://www.work.ua/ru/jobs/3061923/'):
        '''
        Takes main info from vacancy page
        :param link: link to vacancy(str)
        :return: main vacancy info (dict) !keys you can see in return
        '''
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
        '''
        Parse all possible pages with current search request for last 30 days. And write it to self.filename
        :return: None
        '''
        try:
            with open(self.filename, 'a') as file:
                pass
        except FileNotFoundError:
            with open(self.filename, 'w') as file:
                pass

        page1 = self.get_page(1)
        max_pages = self.get_numbers_of_pages(page1)
        with open(self.filename, 'a') as file:
            for i in range(0, max_pages):
                links = self.get_links_from_page(page1)
                for link in links:
                    print(f'-> working! page: {i+1}')
                    info = self.get_info_via_link(link)
                    write_info = f'Vacancy:{info["vac"]}\nPayment:{info["pay"]}\nCompany:{info["company"]}\n' \
                                 f'Place:{info["place"]}\nLink:{info["link"]}\n\n'
                    file.write(write_info)
                page1 = self.get_page(i+1)

            file.write('\n__FROM_DICH_WITH_LOVE__')
        return None

if __name__ == '__main__':
    a = ParseWorkUa('python', 10000, 30000, 'save.txt')
    a.parse_all_and_save()
