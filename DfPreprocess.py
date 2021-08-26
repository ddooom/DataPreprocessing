import pandas as pd

# pandas DataFrame 전처리를 위한 기능 단위 모듈 
class DfMethods:
    '''
    * Function Naming Rules
        - Set... : 열의 추가 없이 입력한 열의 값만 변형
        - Get... : 입력한 데이터프레임을 변형시켜 다른 데이터프레임을 반환
        - Add... : 새로운 열을 추가
    '''

    @classmethod
    def SetDatetime(cls, df: pd.DataFrame, date_col:str, date_format:str):
        '''
        * description : 데이터프레임 내의 시간을 나타내는 열을 datetime 타입으로 변환
        
        - df : pandas 데이터프레임
        - date_col : datetime 열
        - date_format : datetime 열의 datetime 형태
        
            %a : Weekday, abbreviated (Mon, Tues, Sat)
            %A : Weekday, full name (Monday, Tuesday, Saturday)
            %d : Day of month, zero-padded (01, 02, 21)
            %b : Month abbreviated (Jan, Feb, Sep)
            %B : Month, full name (January, Feburary, September)
            %m : Month number, zero-padded (01, 02, 09)
            %y : Year, without century, zero-padded (02, 95, 99)
            %Y : Year, with century (1990, 2020)
            %H : Hour(24 hour), zero padded (01, 22)
            %M : Minute, zero-padded (01, 02, 43)
            %S : Second, zero padded (01, 32, 59)

            etc) https://www.dataindependent.com/pandas/pandas-to-datetime/
        '''
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], format=date_format)
        
        print('SetDatetime done.')
        return df
        
    
    @classmethod
    def GetRowIncludeKeyword(cls, df: pd.DataFrame, target_col: str, keyword: str or list, logic: str=None):
        '''
        * description : 특정 열(target_col)에 keyword가 포함된 행만 추출
        
        - df : pandas 데이터프레임
        - target_col : keyword 존재 여부를 파악할 열
        - keyword : 존재 여부를 파악할 키워드
        - logic : 복수 키워드일 경우, 모든 키워드를 가진 행만 추출할지, 하나만 가지면 추출할지 여부 ('and', 'or')
        '''
        df = df.copy()
        
        if isinstance(keyword, str):
            df = df[df[target_col].apply(lambda r: keyword in r)]
        
        elif isinstance(keyword, list):
            idx = df[target_col].apply(lambda r: keyword[0] in r)
            if logic == 'and':
                for k in keyword[1:]:
                    idx = idx & df[target_col].apply(lambda r: k in r)
                    
            elif logic == 'or':
                for k in keyword[1:]:
                    idx = idx | df[target_col].apply(lambda r: k in r)
                
            else:
                raise ValueError("If keyword is list, Then logic must be 'and' or 'or'")
        
            df = df[idx]
        
        print('GetRowIncludeKeyword done.')
        return df
    
    @classmethod
    def GetRowExcludeKeyword(cls, df: pd.DataFrame, target_col: str, keyword: str or list, logic: str=None):
        '''
        * description : 특정 열(target_col)에 keyword가 포함되지 않는 행만 추출
        
        - df : pandas 데이터프레임
        - target_col : keyword 존재 여부를 파악할 열
        - keyword : 존재 여부를 파악할 키워드
        - logic : 복수 키워드일 경우, 모든 키워드를 가진 행만 추출할지, 하나만 가지면 추출할지 여부 ('and', 'or')
        '''
        df = df.copy()
        
        if isinstance(keyword, str):
            df = df[df[target_col].apply(lambda r: keyword not in r)]
        
        elif isinstance(keyword, list):
            idx = df[target_col].apply(lambda r: keyword[0] not in r)
            if logic == 'and':
                for k in keyword[1:]:
                    idx = idx & df[target_col].apply(lambda r: k not in r)
                    
            elif logic == 'or':
                for k in keyword[1:]:
                    idx = idx | df[target_col].apply(lambda r: k not in r)
                
            else:
                raise ValueError("If keyword is list, Then logic must be 'and' or 'or'")
        
            df = df[idx]
        
        print('GetRowExcludeKeyword done.')
        return df
    
    @classmethod
    def GetCountEachDate(cls, df: pd.DataFrame, date_col: str, period: str, drop_zero: bool=False, date_ascending: bool=False):
        '''
        * description : period 별 행의 개수 데이터프레임 반환, 시간 별 정렬되어 출력 
        
        - df : pandas 데이터프레임
        - date_col : datetime 열 (꼭 datetime 타입이어야 함)
        - period : 어떤 기간 별로 데이터를 출력할 것인지 설정 (일별: 'd', 주별:'w', 월별:'m', 연별:'y')
        - drop_zero : 일별, 월별 등으로 나타내었을 때, 행 수가 0인 date 제거 여부
        - date_ascending : 시간 별로 정렬할 때, 오름차순 여부
        '''
        
        df = pd.DataFrame(df.groupby(date_col)[df.columns[0]].count())
        df.columns = ['count']
        
        if period in ['d', 'D']: df = df.resample('D').sum()
        elif period in ['w', 'W']: df = df.resample('W-Sun').sum()
        elif period in ['m', 'M']: df = df.resample('M').sum()
        elif period in ['y', 'Y']: df = df.resample('Y').sum()
        else: raise(ValueError("Incorrect period, period must be one of ['d', 'w', 'm', 'y']"))
        
        if drop_zero:
            df = df[df['count']!=0]
        
        df = df.sort_values(by=date_col, ascending=date_ascending)
        
        print('GetCountEachDate done.')
        return df
    
    @classmethod
    def GetCountEachChannel(cls, df: pd.DataFrame, channel_col: str, sorting_by_cnt: str=None, set_percentage: bool=False):
        '''
        * description : channel 별 행의 개수 데이터프레임 반환
        
        - df : pandas 데이터프레임
        - channel_col : groupby 기준이 될 열
        - sorting_by_cnt : count 기준으로 정렬 여부 (오름차순정렬 : 'ascending', 내림차순정렬 : 'descending', 정렬x : 그 외 문자열)
        - set_percentage : 열별 count의 비중을 백분율로 나타내어 열로 추가 
        '''
        
        df = pd.DataFrame(df.groupby(channel_col)[df.columns[0]].count())
        df.columns = ['count']
        
        if sorting_by_cnt=='ascending': df = df.sort_values(by='count', ascending=True)
        elif sorting_by_cnt=='descending': df = df.sort_values(by='count', ascending=False)
        
        if set_percentage:
            df['percentage'] = round(df['count'] * 100 / df['count'].sum(), 4)
        
        print('GetCountEachChannel done.')
        return df
    
    @classmethod
    def AddCafeNameInURL(cls, df: pd.DataFrame, URL_col):
        '''
        * description : 카페 URL만을 가진 데이터프레임을 입력받아 'cafe.com/카페이름' 형태의 값을 가진 열 추가
        
        - df : pandas 데이터프레임 (URL 열은 카페 URL만을 포함하고 있어야 함)
        - URL_col : URL을 포함하고 있는 열
        '''
        
        df = df.copy()
        URLs = df[URL_col]
        
        if sum(['cafe' not in r.split('/')[2] for r in URLs]):
            raise ValueError('URL values must be cafe URL')
        
        df = df.copy()
        df['CafeName'] = ["/".join(r.split('/')[2:4]) for r in URLs]
        
        print('AddCafeNameInURL done.')
        return df


# 예제) DfMethods를 이용한 pandas DataFrame 전처리 파이프라인 
class DfPipeline:
    '''
    * DfBase를 활용하여 특정 프로젝트에서만 사용하는 파이프라인 설정
    '''
    
    @classmethod
    def CountRowIncludeKeywordEachMonth(cls, df: pd.DataFrame, target_col: str, keyword: str or list, logic: str=None):
        '''
        * 월별 target_col에 keyword가 포함된 행의 개수
        
        - df : pandas 데이터프레임
        - target_col : keyword 존재 여부를 파악할 열
        - keyword : 존재 여부를 파악할 키워드
        - logic : 복수 키워드일 경우, 모든 키워드를 가진 행만 추출할지, 하나만 가지면 추출할지 여부 ('and', 'or')
        '''
        
        df = df.copy()
        df = DfMethods.SetDatetime(df, 'date', '%y.%m.%d.') # 해당 프로젝트에서만 사용되는 데이터이므로 date_col을 함수 내에 입력
        df = DfMethods.GetRowIncludeKeyword(df, target_col, keyword, logic)
        df = DfMethods.GetCountEachDate(df, 'date', 'm', False, True)
        
        return df
    
    @classmethod
    def CountRowEachServeralColumns(cls, df: pd.DataFrame, target_cols: list, top_n: int, set_percentage: bool=False):
        '''
        * 복수의 열을 입력 받아 열의 값별 행의 개수를 정렬하여 상위 n개만 반환
        
        - df : pandas 데이터프레임
        - target_cols : 값별 행의 개수를 구할 복수의 열
        - top_n : 내림차순 정렬했을 때, 반환할 행의 수
        '''
        
        df = df.copy()
        line = pd.DataFrame(['|' for _ in range(top_n)], columns=['|'])
        cnts = [line]
        for c in target_cols:
            cnts.append(DfMethods.GetCountEachChannel(df, c, 'descending', set_percentage).head(top_n).reset_index())
            cnts.append(line)
        
        return pd.concat(cnts, axis=1)
    
    @classmethod
    def CountRowEachCafe(cls, df: pd.DataFrame):
        '''
        * URL에서 카페 이름을 따서 이름 별 행의 수 반환
        
        - df : pandas 데이터프레임
        '''
        
        df = df.copy()
        df = DfMethods.AddCafeNameInURL(df[df['채널2']=='카페'], 'URL1')
        df = DfMethods.GetCountEachChannel(df, 'CafeName', 'descending', True)
        
        return df