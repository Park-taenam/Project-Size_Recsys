# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# 시각화 관련
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from collections import Counter
from PIL import Image
from matplotlib import rc

# 그래프에서 한글 폰트 깨지는 문제에 대한 대처(전역 글꼴 설정)
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings(action='ignore') 

import matplotlib
matplotlib.rcParams['font.family'] ='Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] =False

#nlp
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from selenium import webdriver
from tqdm.notebook import tqdm
import time, urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
keys = Keys()
import re, os, sys, json

from hanspell import spell_checker

from konlpy.tag import Kkma #형태소분석
from konlpy.tag import Okt #형태소분석
import soynlp; from soynlp.normalizer import * #정규화
# from pykospacing import Spacing------------------>써야함!
# spacing = Spacing()------------------------------>써야함!

from konlpy.tag import Komoran, Hannanum, Kkma, Okt
komoran = Komoran(); hannanum = Hannanum(); kkma = Kkma(); okt = Okt();

# %%
def crawlingdataconcat():
    df = pd.DataFrame()
    for i in range(1,21,1):
        try:
            df_before = pd.read_csv('data/hood_'+str(i)+'page.csv') #크롤링파일 불러오기
            print('df',str(i),': ',df_before.shape)
        except:
            df_before = pd.DataFrame() #아직크롤링되지 않은파일은 빈 df
            print('df',str(i),': ',df_before.shape)
            
        df = pd.concat([df,df_before]) #합치기
            

            
    print('df : ', df.shape)
    df.drop_duplicates(subset = None,keep = 'first', inplace = True,ignore_index = True)
    print('중복제거df : ', df.shape)#전체열이 같은 중복제거
    #성별, 키,몸무게 모두 null아니고 수치종류 적어도 하나 값이 있는 것들 filter
    df = df[~df['gender'].isnull()&~df['height'].isnull()&~df['weight'].isnull()&
                                      (~df['총장'].isnull()|
                                       ~df['어깨너비'].isnull()|~df['가슴단면'].isnull()|
                                       ~df['소매길이'].isnull())]
    print('최종사용 data:{}'.format(df.shape))
    print('-'*10)
    return df

def crawlingdataprocessing(df):
    #kg,cm제거 및 수치타입으로 변경
    df["height"]=df["height"].replace('cm','',regex = True)
    df["weight"]=df["weight"].replace('kg','',regex = True)
    df= df.astype({'height':'float','weight':'float'})
    print('df전처리완료')
    print('-'*10)
    return df

def add_reviewcol(df):
    df = df.drop_duplicates(subset=['content'])#리뷰중복제거
    print('같은내용리뷰 중복제거 완료')
    df.reset_index(drop=True, inplace=True)

    df['review'] = str('')
    #외국어 리뷰 삭제
    i = 0; nohangul = []
    for i in range(df.shape[0]):
        text = re.sub('[^ㄱ-ㅣ가-힣]', '',df.iloc[i,8])
        if(text==''):
            nohangul.append(i)
    df = df.iloc[[True if i not in nohangul else False for i in range(df.shape[0])],:]
    df.reset_index(drop=True, inplace=True)

    i=0
    for i in range(df.shape[0]):
        text = df.iloc[i,7]
        text = re.sub(pattern='[^\w\s\n]', repl='', string=text) #특수문자 제거
        text = re.sub(pattern='[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z]', repl=' ', string=text) #숫자, 그이외 삭제
        text = re.sub(pattern='[ㄱ-ㅎㅏ-ㅣ]+', repl='', string=text) #단순 모음, 자음 삭제
        text = repeat_normalize(text, num_repeats=2) #불필요반복문자정규화
        #text = spacing(text) #띄어쓰기------------------------>써야함!
        df['review'][i] = text
    print('리뷰 전처리 열 추가')
    print('df shape:{}'.format(df.shape))
    print('-'*10)
    return df
# %%
# 두개의 사전이 합치고 나서 진행
# 중복제거
# 'n+2'개의 최종 리스트가 생성됨
def sizedict_nodup(oneOfRawList):
    print('중복제거 전:{}개'.format(len(oneOfRawList)))
    oneOfRawList = set(oneOfRawList)
    print('중복제거 후:{}개'.format(len(oneOfRawList)))
    print('-'*10)
    return list(oneOfRawList)


#최종 사이즈 사전 완성
def final_sizedict(size_figure_list):
    all_big = {}
    all_small = {}
    for i in size_figure_list:
        all_big[i] = big
    
    for i in size_figure_list:
        all_small[i] = small
    
    return all_big,all_small
# %%
df = crawlingdataconcat()
df = crawlingdataprocessing(df)
df = add_reviewcol(df)
#df.to_csv('data/hood_1to20.csv', encoding="UTF-8", index=False) #파일로 저장
# %%
total_big,total_small           = final_sizedict(total)
chongjang_big,chongjang_small   = final_sizedict(chongjang)
shoulder_big,shoulder_small     = final_sizedict(shoulder)
arm_big,arm_small               = final_sizedict(arm)
chest_big,chest_small           = final_sizedict(chest)