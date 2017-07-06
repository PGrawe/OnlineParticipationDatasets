import scrapy
from selenium import webdriver
from OnlineParticipationDataset import items
from datetime import datetime
from itertools import count


class BraunkohleSpider(scrapy.Spider):
    name = "braunkohle"
    tree = True
    custom_settings = {"DOWNLOADER_MIDDLEWARES": {'OnlineParticipationDataset.middlewares.JSMiddleware': 543,},
                       "ITEM_PIPELINES": {
                          # 'OnlineParticipationDataset.pipelines.OnlineparticipationdatasetPipeline': 300,
                          'OnlineParticipationDataset.pipelines.JsonWriterPipeline': 300,
                          'OnlineParticipationDataset.pipelines.TreeGenerationPipeline': 400

                       }}
    urls = [      'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/11',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/12',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/13',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/14',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/17',
                  'https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/16']
    start_urls = ['https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/9']
    # urls = ['https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/14']
    # start_urls = ['https://www.leitentscheidung-braunkohle.nrw/perspektiven/de/home/beteiligen/draftbill/47589/para/17']
    def __init__(self, **kwargs):
        super(BraunkohleSpider, self).__init__(**kwargs)
        self.id_counter=count(start=0, step=1)
        self.link_counter=iter(self.urls)
        self.suggestions_counter=0
        self.comments_counter=0
        # self.driver = webdriver.Firefox()

    def extract_num_comments(self, response):
        '''
        Extracts the number of comments given a response on thread-level
        :param response: Response
        :return: Number of comments as a string
        '''
        self.log('Number of comments:\n')
        self.log(response.css('.row.ecm_commentsHead h2::text').extract())
        return response.css('.row.ecm_commentsHead h2::text').extract()[0].split(' ')[1].strip('()')

    def get_category(self, response):
        '''
        Returns category by manually deciding on the link
        :param response: Response
        :return: category (string)
        '''
        url = response.url
        num = int(url.split('/')[-1])
        cases = {
            9: 'Energie',
            11: 'Umwelt',
            12: 'Holzweiler',
            13: 'Holzweiler',
            14: 'Holzweiler',
            17: 'Holzweiler',
            19: 'Strukturwandel im Rheinischen Revier',
        }
        return cases.get(num, 'Unknown')

    def create_suggestion_item(self, response):
        '''
        Creates a suggestion item based on information in response
        :param response: scrapy response
        :return: suggestion item
        '''
        self.suggestions_counter+=1
        sug_item = items.SuggestionItem()
        #sug_item['id'] = response.css('.ecm_draftBillParagraphTabs>div>div>div::attr(id)').extract_first()
        sug_item['id'] = next(self.id_counter)
        sug_item['title'] = ' '.join(response.css('.ecm_draftBillParagraphContent.push-top>h1::text').extract())
        sug_item['content'] = ' '.join(response.css(
            '.ecm_draftBillParagraphContent.push-top>div>h3::text,.ecm_draftBillParagraphContent.push-top>div>p>strong::text').extract())
        sug_item['comment_count'] = int(self.extract_num_comments(response))
        sug_item['category'] = self.get_category(response)
        sug_item['parent'] = 'None'
        sug_item['children']=[]
        return sug_item

    def get_datetime(self, comment):
        '''
        Returns datetime of comment
        :param comment: comment (selector)
        :return: datetime
        '''
        com_details = comment.css('.ecm_commentDetails')
        date_time = ' '.join(com_details.css('.ecm_commentDate span::text').extract())
        return datetime.strptime(date_time, "%d.%m.%Y %H:%M")

    def get_author(self, comment):
        '''
        Returns author of comment
        :param comment: comment (selector)
        :return: name of author (string)
        '''
        com_details = comment.css('.ecm_commentDetails')
        return com_details.css('.ecm_userProfileLink span::text').extract_first()

    def get_voting(self, comment):
        '''
        Returns voting (likes) of comment
        :param comment: comment (selector)
        :return: number of likes (string)
        '''
        com_rating = comment.css('.ecm_commentRating .ecm_rate')
        return com_rating.css('span::text').extract_first()

    def get_content(self, comment):
        '''
        Returns written content of comment as a string
        :param comment: commment (selector)
        :return: content (string) of comment
        '''
        return ' '.join(comment.css('.ecm_commentContent p::text').extract())

    def has_children(self, comment):
        '''
        Checks if comment has children
        :param comment: comment (selector)
        :return: true if comment has children, else: false
        '''
        comment_type = comment.css('::attr(class)').extract()[0]
        if 'ecm_comment_children' in comment_type:
            return True
        else:
            return False


    def get_children_comments(self, comment_sublist):
        '''
        Returns a list of all comments in a comment sublist
        :param comment_sublist: comment-sublist (selector)
        :return: List of all comments (first level)
        '''
        # return comment_sublist.css('.ecm_commentSublist>.ecm_comment')
        return comment_sublist.xpath("div[@class='row ecm_comment' or @class='row ecm_comment ecm_comment_children']")

    def get_children_sublists(self, comment_sublist):
        '''
        Returns a list of all sublists in a comment sublist
        :param comment_sublist: comment-sublist (selector)
        :return: List of all sublists (first level)
        '''
        # return comment_sublist.css('.ecm_commentSublist>.ecm_commentSublist')
        return comment_sublist.xpath("div[@class='ecm_commentSublist']")

    def create_comments(self, comments, comment_sublists, parent_id):
        '''
        Creates comment items recursively based on given list of comments (selectors) and list of comment-sublists (selectors)
        :param comments: list of comments (selectors)
        :param comment_sublists: list of comment-sublists (selectors)
        :param id: ID of parent comment (For top level comments the id of the suggestion)
        :return: list of items to be yielded
        '''
        comment_list = []
        sub_iterator = iter(comment_sublists)
        for comment in comments:
            self.comments_counter+=1
            # Populate current item
            tmp_comment = items.CommentItem()
            tmp_comment['author'] = self.get_author(comment)
            tmp_comment['date_time'] = self.get_datetime(comment)
            tmp_comment['id'] = next(self.id_counter)
            tmp_comment['parent'] = parent_id
            tmp_comment['content'] = self.get_content(comment)
            tmp_comment['vote'] = self.get_voting(comment)
            tmp_comment['children'] = []
            # Check if comment has children
            if self.has_children(comment):
                # Get next sublist (contains children comments)
                comment_sublist = next(sub_iterator)
                # Add child-ids to current comment
                #tmp_comment['children'] = self.get_child_ids(comment_sublist)
                # Recursively call function with child comments and sublists
                children_comments = self.get_children_comments(comment_sublist)
                children_sublists = self.get_children_sublists(comment_sublist)
                children = self.create_comments(children_comments, children_sublists, tmp_comment['id'])
                # Add child comments to list
                comment_list.extend(children)
            # Add current comment to list
            comment_list.append(tmp_comment)
        return comment_list

    def parse(self, response):
        '''
        Parses thread-level information
        :param response: Response
        :return: Yields items and new requests
        '''
        # Create, populate and yield suggestion item:

        suggestion = self.create_suggestion_item(response)
        yield (suggestion)
        # Get comments (regular and with child comments):
        initial_comments = response.css('#comment-area>div>.ecm_comment')
        # Get comment sublists (each corresponds to one comment with child comments in <comments>)
        initial_comment_sublists = response.css('#comment-area>div>.ecm_commentSublist')
        initial_id = suggestion['id']
        comments = self.create_comments(initial_comments, initial_comment_sublists, initial_id)
        for comment in comments:
            yield comment
        try:
            next_url = next(self.link_counter)
            yield scrapy.Request(url=next_url,callback=self.parse)
        except Exception:
            self.log("No more links.")
