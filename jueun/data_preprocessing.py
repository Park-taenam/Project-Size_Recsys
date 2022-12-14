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
            print('df',str(i),': ',df_before.shape,end = ',')
        except:
            df_before = pd.DataFrame() #아직크롤링되지 않은파일은 빈 df
            print('df',str(i),': ',df_before.shape)
            
        df = pd.concat([df,df_before]) #합치기
            

            
    print('모두합친df : ', df.shape)
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
df = crawlingdataconcat()
df = crawlingdataprocessing(df)
df_before_nlp = add_reviewcol(df)
df_before_nlp_origin = df_before_nlp.copy()
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
# %%
total = ['사이즈','사이즈하','사이즈감','임사이즈','여사이즈','사이즌','뻐요사이즈','싸이즈','핏이','핏','핏입니다',
      '핏감도','핏나','핏감이랑','핏처럼','핏입니당','핏이에요','핏이예요','핏이랑','핏이구요','핏이네요','핏감은',
      '핏입니','핏이라서','핏으로','옷핏','핏더','핏도','핏감','옷','후드','후드티','핏은','좋아요핏','요핏도',
      '좋아요핏도','상의','요핏','폼','폭','사이즈','후드','옷','품','전체','품도','몸통','옷핏','상체','핏',
      '핏이구','핏이었','핏임','핏입',
      '핏입니','핏감','요핏','폼','후드핏','핏이','크기','상품','상의','핏더']
chongjang = ['길이','기장','총장','궁디','궁딩','엉덩이','밑','밑단','위아래','끝단','밑기장',
             '밑단이랑','기장이','기장입니','밑단','밑','기장감','요기장','총길이','총장','총기장',
            '길이감','끝','기장','길이']
shoulder = ['어깨핏','어께','어깨','너비','어깡','골격','바디','가로','넓이','등판','통',
            '어깨깡패','어깨라','어깨넓','어깨쪽','어께','몸집','어깨핏','어깨선','어깨라인','어깡',
            '어깨','통','몸통','골격','넓이','너비','등판']

chest = ['가슴','둘레','바디','가로','넓이','통','둘레','몸집','가슴팍','통','몸통']
arm = ['소매','팔도','손목','손','팔다리','팔목','팔','팔꿈치','팔이','요팔',
       '당팔','팔길이','팔다리','팔길','팔소매','손목','팔목','소매통','손','팔','소매','팔기장']

small = ['작습니다','짧았어요','짧습니다','짧으면','짧','작았어요','짧다고','쪼여서','작았으면',
      '작아도','작으면','작음','작아진','좁다고',
      '짧아요','짧게','짧다는','좁다는','작네','작기는','달라붙는','작은데','짧은데','짧음',
      '작긴','짧네요','작게','작아서','작은','짧고','짧아','좁은','타이트','짧았지만','붙어서','짧긴',
      '작은것','작아요','짧은','짧아서','짧지만','좁아','좁고','작네요','작아','쪼이는','좁아요','크롭느낌',
      '크롭하','작고','숏','쫄려','작다고','작다','좁아서','작','크롭','크롭된','미니','크롭해',
      '길었으면','컸으면','좁게','짧지' ,'작지','크롭이','핏되',
      '숏하','사이즈업하','크롭하','숏한','크롭하긴','크롭이','크롭해','크롭느낌','크롭된','사이즈업','짝',
       '작','숏','짧긴','크롭','크롭한','타이트','크롭이라','작긴',
       '작','짧','좁']

big = ['큰','긴','커요','크고','크긴','넉넉하고','길어서','넉넉하게','작다는'
     '넉넉한','클','길고','큰데','크지','크지만','부해','크니깐','크더라구요','컸어도','넓음','큼직하게',
     '박시하네요','넉넉할','헐렁하게','큼직하니','컸음','큽니','긴데','길어','길게','넓어서','넓어','박시하고','컸어요',
     '박시','크다고','크다는','넓게','넓고','커용','길다는','크지도','큼','크다','길었어요','넉넉함','큰데도','덮는데',
     '덮이고','컸고','벙벙해서','크더라고요','컸을','크거나','크더라','컸었는데','컸어용','컸습니다','덮네요',
     '큼지막해서','덥는','박시하게','크네요','클까','넉넉하구','박시하','컸는데','넉넉하네요','크게','크니까','넉넉한데','길어요',
     '컸지만','헐렁한','크네','넉넉해','펑퍼짐한','덮어용','박시하니','헐렁해','넉넉하지''넉넉하구요','커','큽니다','넉넉하니',
     '크','길지','박시한데','덮어요','길긴','넉넉해요','넓은','덮히는', '넓긴','덮어줘서','덮은','넉넉해서','큼직해서','기네','낙낙',
     '흘러내리는','덮어서','벙벙한','커서','큰것','박시핏','오퍼핏','낙낙해','여유핏','널널함','길','덮어','넉넉합니다','크면',
     '덮고','가오리','루즈핏','펑퍼짐','길었지만','헐렁하고','남아','아방핏','박스핏','널널','오바핏','덮습니다','넉넉히',
     '헐렁해서','접어도','접어','접어서','널','넓어요','덮고도','오버','와이드','낭낭','헐렁','접으면','짧았으면','접고',
     '버핏','접어야','잡아먹힌','수선해서','오버핏','오버사이즈','오버사이징해서','낙낙하다','낙낙한데','낙낙해요','오버핏이예요','오버핏입니당',
       '요박시하','컸어용','낙낙합니','어벙벙하','와이드핏','크니깐','크네요옷','널널해요','오버핏나와요','널럴하',
       '요넉넉하','엄청큼','여유핏','오버느낌','아방핏','오버핏은','넓긴','넉넉함','입니다오버핏','큽니다오버핏',
       '큽니다제','큽니당','오버해요','요박시한','헐렁하긴','헐렁거리','아방방한','아방방','박시합니','박시했다',
       '빅사이즈','받았습니다오버핏','빡시하','루즈핏으로','낭낭한','오버핏이긴','박스핏','널널함','어벙벙',
       '요넉넉한','오퍼핏','오버핏이구요','낙낙해','낭낭해서','넉넉하구','넉넉한데','아방해','오버핏이라서',
       '낭낭하','박시해','커용','넉넉해','펑퍼짐','박시하지','널널','좋아요오버핏','어벙벙한','널널하','오바핏',
       '오버하지','오버핏하','박시합니다','오버핏되','박시함','버핏','박시한','낙낙하니','박시해요','크네용',                     '낙낙해서','큼직해서','루즈해','느슨','널널합니다','아방아','아방아방','루즈핏이','박시하','세미오버',
       '세미오버핏','루즈해서','오버핏이라','루즈핏이라','오버핏이네요','오버핏입니','어벙','오버해','박시한데',
       '아방','오버핏이에요','예뻐요오버핏','큼지막','박시핏','오버해서','루즈한','오버핏인데','넉넉하구요','박시할',
       '큼직','오버한','오버핏이','낙낙하','아방하','롱','오버핏으로','낙낙한','오버핏입니다','박시해서','와이드',                     '요오버핏','넉넉해서','큽니','오버','오버하','루즈','루즈핏','박시','넉넉','길','크긴','아방한','널널한',
       '헐렁','길긴','와이드하','아방해서','세미오버사이즈',             
       '크','길','널','덮','넓','벙벙하','덮이','덮히','커다랗','덥히','넉넉해지','뒤집'             
       '넉넉']
# %%
total     = sizedict_nodup(total)
chongjang = sizedict_nodup(chongjang)
shoulder  = sizedict_nodup(shoulder)
arm       = sizedict_nodup(arm)
chest     = sizedict_nodup(chest)
small     = sizedict_nodup(small)
big       = sizedict_nodup(big)
# %%
#total,chongjang,shoulder,chest,arm ->keywords리스트

from tqdm import tqdm
def get_keywords(keywords, df,keyword_column_name):
    start = time.time()
    review = df['review']
    df['new_column'] = str('')
    for i in tqdm(range(len(review))):
        # if i % 1000 ==0:
        #     print("{}번째 리뷰 완료(천 단위) : ".format(i))
        keywords_search = []
        for j in keywords:
            if re.findall(j, review[i]):
                a = re.findall(j +'+[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+\s+[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+\s+[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+',review[i]) #키워드 +단어
                aa = re.findall(j + ' '+'+[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+\s+[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+\s+[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+',review[i])#키워드 +띄고 단어
                b = re.findall('[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+' + j ,review[i]) #단어 + 키워드
                bb = re.findall('[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+\s+' + j ,review[i])#단어 + 띄고 키워드
                #bb = re.findall('[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+\s+' +' '+ j ,review[i])
                keywords_search.extend(a)
                keywords_search.extend(aa)
                keywords_search.extend(b)
                keywords_search.extend(bb)
                # print(i,'번째',j,a,end='|')
                # print(aa,end='|')
                # print(b,end='|')
                # print(bb)
        #print(i,'번째 리스트:',keywords_search)
        #print('-'*10)
        
        if len(keywords_search) != 0:
            keywords_o = ','.join(x for x in keywords_search)
            df['new_column'][i] = keywords_o 
            
        else:
            df['new_column'][i] = '0'
    
    a = df.rename(columns = {'new_column':keyword_column_name})
    end = time.time()
    print("{:.5f} sec".format(end-start))
    return a[keyword_column_name]
# %%
#total,chongjang,shoulder,chest,arm ->keywords리스트
keyword_column_name = 'total_keyword'
df_total            = get_keywords(total,df_before_nlp,keyword_column_name)
keyword_column_name = 'chongjang_keyword'
df_chongjang        = get_keywords(chongjang,df_before_nlp,keyword_column_name)
keyword_column_name = 'shoulder_keyword'
df_shoulder         = get_keywords(shoulder,df_before_nlp,keyword_column_name)
keyword_column_name = 'chest_keyword'
df_chest            = get_keywords(chest,df_before_nlp,keyword_column_name)
keyword_column_name = 'arm_keyword'
df_arm              = get_keywords(arm,df_before_nlp,keyword_column_name)

df_keywords         = pd.concat([df_before_nlp,
                                 df_total,
                                df_chongjang,
                                df_chest,
                                df_shoulder,
                                df_arm],axis = 1)
df_keywords =df_keywords.drop(['new_column'],axis = 1)
df_keywords_origin =df_keywords.copy()
# %%
df_keywords.info()
# %%
#small,big
def big_small(big,small,df,name_big_small):
    start = time.time()
    review = df[name_big_small+'_keyword']
    df[name_big_small + '_big'] = str('')
    df[name_big_small + '_small'] = str('')
    for i in tqdm(range(len(review))):
        # if i % 1000 ==0:
        #     print("{}번째 리뷰 완료(천 단위) : ".format(i))
        big_search = []
        small_search = []
        for j in big:
            if re.findall(j, review[i]):
                a = re.findall(j,review[i]) #키워드
                big_search.extend(a)
               
        for j in small:
            if re.findall(j, review[i]):
                a = re.findall(j,review[i]) #키워드
                small_search.extend(a)
            
               
        
        if len(big_search) != 0:
            df[name_big_small + '_big'][i] = 1
            
        else:
            df[name_big_small + '_big'][i] = 0
        
        if len(small_search) != 0:
            df[name_big_small + '_small'][i] = 1
            
        else:
            df[name_big_small + '_small'][i] = 0
        #time.sleep(0.2)
    
    #df.rename(columns = {'keyword_column_name':keyword_column_name},inplace=True)
    end = time.time()
    print("{:.5f} sec".format(end-start))
    return df[[name_big_small + '_big',name_big_small + '_small']]
# %%
name_big_small      = 'total'
total_big_small     = big_small(big,small,df_keywords,name_big_small)
name_big_small      = 'chongjang'
chongjang_big_small = big_small(big,small,df_keywords,name_big_small)
name_big_small      = 'arm'
arm_big_small       = big_small(big,small,df_keywords,name_big_small)
name_big_small      = 'chest'
chest_big_small     = big_small(big,small,df_keywords,name_big_small)
name_big_small      = 'shoulder'
shoulder_big_small  = big_small(big,small,df_keywords,name_big_small)

final_df            = df_keywords
final_df_origin     = final_df.copy()