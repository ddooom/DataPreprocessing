import numpy as np
import pandas as pd

import re
import kss
from pykospacing import Spacing
from hanspell import spell_checker
from soynlp.normalizer import *

from konlpy.tag import Mecab, Okt, Kkma, Hannanum
from ckonlpy.tag import Twitter
from tqdm.notebook import tqdm
import copy
import warnings
import os
import sys
from collections import defaultdict

import matplotlib.pyplot as plt
from wordcloud import WordCloud

class KoNLPMethods:
    
    @classmethod
    def SplitSentence(cls, texts: list):
        '''
        * description : 입력받은 texts를 문장 단위로 분할
        '''
        
        n = len(texts)
        processed_texts = []
        for idx, text in enumerate(texts):
            processed_texts.extend(kss.split_sentences(text))
            print(f'* Spliting Sentences... ({idx+1}/{n})', end='\r')
        print('* Spliting Sentences Done.                 ')
        
        return processed_texts
    
    @classmethod
    def ModifyPunct(cls, texts: list):
        '''
        * description : 입력받은 texts에 존재하는 툭수문자 수정
        '''
        
        punct = "/-'?!.,#$%\'()*+-/:;<=>@[\\]^_`{|}~" + '""“”’' + '∞θ÷α•à−β∅³π‘₹´°£€\×™√²—–&'
        punct_mapping = {"‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", "√": " sqrt ", "×": "x", "²": "2", "—": "-", "–": "-", "’": "'", "_": "-", "`": "'", '“': '"', '”': '"', '“': '"', "£": "e", '∞': 'infinity', 'θ': 'theta', '÷': '/', 'α': 'alpha', '•': '.', 'à': 'a', '−': '-', 'β': 'beta', '∅': '', '³': '3', 'π': 'pi', }
        specials = {'\u200b': ' ', '…': ' ... ', '\ufeff': '', 'करना': '', 'है': ''}
        
        n = len(texts)
        processed_texts = []
        for idx, text in enumerate(texts):
            for p in punct_mapping:
                text = text.replace(p, punct_mapping[p])
            for p in punct:
                text = text.replace(p, f' {p} ')
            for s in specials:
                text = text.replace(s, specials[s])
            processed_texts.append(text.strip())
            print(f'* Modifing Punctuations... ({idx+1}/{n})', end='\r')
        print('* Modifing Punctuations Done.                 ')
        
        return processed_texts
        
    @classmethod
    def RemovePunct(cls, texts: list):
        '''
        * description : 입력받은 texts에 존재하는 툭수문자 제거
        '''
        
        n = len(texts)
        processed_texts = []
        for idx, text in enumerate(texts):
            text = re.sub(r'[@%\\*=()/~#&\+á?\xc3\xa1\-\|\.\:\;\!\-\,\_\~\$\'\"]', '',str(text)) #remove punctuation
            text = re.sub(r'\d+','', str(text))# remove number
            text = text.lower() #lower case
            text = re.sub(r'\s+', ' ', text) #remove extra space
            text = re.sub(r'<[^>]+>','',text) #remove Html tags
            text = re.sub(r'\s+', ' ', text) #remove spaces
            text = re.sub(r"^\s+", '', text) #remove space from start
            text = re.sub(r'\s+$', '', text) #remove space from the end
            processed_texts.append(text.strip())
            print(f'* Removing Punctuations... ({idx+1}/{n})', end='\r')
        print('* Removing Punctuations Done.                 ')
        
        return processed_texts
    
    @classmethod
    def AddSpace(cls, texts: list):
        '''
        * description : 입력받은 texts의 올바른 위치에 띄어쓰기 추가
        '''
        
        spacing = Spacing()
        n = len(texts)
        processed_texts = []
        for idx, text in enumerate(texts):
            processed_texts.append(spacing(text))
            print(f'* Adding Space... ({idx+1}/{n})', end='\r')
        print('* Adding Space Done.                 ')
        
        return processed_texts
    
    @classmethod
    def ModifySpelling(cls, texts: list):
        '''
        * description : 입력받은 texts의 오탈자를 수정
        '''
        
        n = len(texts)
        processed_texts = []
        for idx, text in enumerate(texts):
            spelled_text = spell_checker.check(text)
            processed_texts.append(spelled_text.checked)
            print(f'* Modifing Spelling... ({idx+1}/{n})', end='\r')
        print('* Modifing Spelling Done.                 ')
        
        return processed_texts
    
    @classmethod
    def RemoveRepeat(cls, texts: list):
        '''
        * description : 입력받은 texts 중 중복되는 음절 제거
        '''
        
        n = len(texts)
        processed_texts = []
        for idx, text in enumerate(texts):
            processed_texts.append(repeat_normalize(text, num_repeats=2))
            print(f'* Removing Repeat Text... ({idx+1}/{n})', end='\r')
        print('* Removing Repeat Text Done.                 ')
        
        return processed_texts
    
    @classmethod
    def ModifyLoanword(cls, texts: list):
        '''
        * description : 입력받은 texts의 외래어를 수정
        '''
        
        # 경로에 loanword 파일이 없으면 예외 발생, 해당 txt 파일 어디서 받나요??
        loanword_data_path = '.'
        loanword_data_name = 'confused_loanwords.txt'
        if loanword_data_name not in os.listdir(loanword_data_path):
            raise ValueError('loanword data is not exist in loanword_data_path')
        
        loanword_map = {}
        loanword_data = open(f'{loanword_data_path}/{loanword_data_name}', 'r', encoding='utf-8')
        lines = loanword_data.readlines()
        for line in lines:
            line = line.strip()
            miss_spell = line.split('\t')[0]
            ori_word = line.split('\t')[1]
            loanword_map[miss_spell] = ori_word
            n = len(texts)
            
        processed_texts = []
        for idx, text in enumerate(texts):
            for loanword in loanword_map:
                text = text.replace(loanword, loanword_map[loanword])
            processed_texts.append(text)
            print(f'* Modifing Loanword... ({idx+1}/{n})', end='\r')
        print('* Modifing Loanword Done.                 ')
        
        return processed_texts


# 화제어 추출
class TopicNounsExtractor:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        
    def get_nouns(self, data, content_columns, min_count = 10):
        nouns_counter = defaultdict(int)
        docs = data[content_columns]
        for doc in tqdm(docs):
            nouns = self.analyzer.nouns(doc)
            for noun in nouns:
                nouns_counter[noun] += 1
                
        nouns_counter = {noun : count for noun, count in nouns_counter.items() if count >= min_count}
        nouns_counter_df = pd.DataFrame({'TERMS' : list(nouns_counter.keys()), 'FREQUENCY' : list(nouns_counter.values())}).sort_values(by = 'FREQUENCY', ascending = False).reset_index(drop = True)
        
        self.nouns_counter_df = nouns_counter_df
        
        return self.nouns_counter_df
    
    def get_file(self, path):
        self.nouns_counter_df.to_csv(path, index = False, encoding = 'cp949')
        print("Successfully saved to that path: {}".format(path))


# 워드 클라우드 시각화
def CreateWordCloud(data = None, backgroundcolor = 'white', width = 800, height = 600):
    wordcloud = WordCloud(font_path = '/Library/Font/malgun.ttf', background_color = backgroundcolor,
                         width = width, height = height).generate_from_frequencies(data)
    plt.figure(figsize = (15, 10))
    plt.imshow(wordcloud)
    plt.axis('off')

    plt.show()