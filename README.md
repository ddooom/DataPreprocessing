# 데이터 전처리 모듈

## DfPreprocess.py

- **용도** 
  - pandas DataFrame 전처리, 변형을 위한 모듈 제공
  
- **설명** 
  - 모듈 별 설명은 코드 내 주석 처리
  
- **사용법**
  ```
  from DfPreprocess import DfMethods as dm
  
  df = dm.SetDatetime(df, 'date', '%Y%m%d')
  df = dm.GetCountEachDate(df, 'date', 'm', drop_zero=True, date_ascending=True)
  ```

<br>

## KoNLPreprocess.py

- **용도**
  - 자연어 데이터를 다룰 때, 한국어 문장 처리 모듈 제공 (맞춤법 교정, 특수문자 제거 등)

- **설명**
  - 모듈 별 설명은 코드 내 주석 처리

- **보완 사항**
  - 화제어 추출 클래스와 워드 클라우드 함수는 따로 구현, 차후의 통합 예정<br>
  - `requirements.txt` 추가 예정
