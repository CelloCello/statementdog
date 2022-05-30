# statementdog

## 使用

**所有的操作都在根目錄進行即可**

安裝相關 packages

    $ pip install -r requirements.txt

`.env` 中可以設定相關變數，若 storage 要使用 AWS S3，則 `STOR_TYPE=S3` 並填入其他 aws 資訊，沒有特殊需求就用預設的即可

執行指令如下，為了避免被 ban，所以有加上 sleep time，會跑很久。  
可以至 `config.py` 依照需求調整 `SLEEP_TIME` 與 `RETRY_TIMES` 兩個設定

    $ python app.py

執行中畫面會有 log，靜待完成後，結果會存於 `results` 目錄  
storage 相關的檔案會模擬置於 `results/stock-reports`，依照日期放置

測試使用 pytest，要先安裝測試相關套件

    $ pip install -r requirements-test.txt

要執行測試可下

    $ pytest


### Deploy

目標機器 OS 為 `Ubuntu 22.04` 並假設已經將環境建置好

使用前需先安裝部屬相關套件 `pip install -r deploy/requirements.txt`

部屬命令：

```shell
$ fab -e -r ./deploy/ -H <username>@<ip> --prompt-for-login-password deploy
```

過程中需要輸入密碼

## 實作介紹

### 架構

```shell
.
├── .env                # 環境變數
├── app.py              # 程式入口
├── statementdog
│   ├── action.py
│   ├── config.py
│   ├── fetcher.py
│   ├── parser.py
│   ├── storage.py
│   └── utils           # 打算放有的沒的共用工具函式
└── tests               # 測試
```

由於此次的作業 scope 不大，所以使用較小型的專案規劃方式進行  
主要目標是希望架構清晰、容易擴展、重用性高且避免過度抽象化。

整體的邏輯處理流程會是：

    app.py -> action.py -> fetcher.py -> parser.py


說明如下：

- `app.py` 入口，放在外面是想說程式有可能有不同的進入方式 (如使用 lambda)，所以做的事很單純，目的是希望容易搬遷功能
- `action.py` 流程處理函式集，類似作業說明中的 data flow 那張圖的實作
- `fetcher.py` 資料抓取相關函式，打 api 等的 http request 行為實作在此
- `parser.py` 資料的處理，將 fetcher 取得的東西擷取並轉成後續處理使用的資料格式
- `storage.py` 使用 cloudstorage 實作的 storage 處理介面，兩者在處理完資料存放的位置可能不同 (local disk 或是 AWS S3)，是希望能顧及 local 開發以及 production，不用作多餘的處理，利用 `.env` 來設定

### 關於 .env

用來管理設定不同環境所需的變數，像是 local, staging, production，而不需變動程式

這邊的例子是 storage 相關設定  
local 就存放在本機某個目錄下
staging / production 可能會存在某個 cloud storage 如 AWS S3，但這兩者又可分開設定

可以在 deploy 時依照不同的目標環境給予不同的 `.env`，也可以避免暴露重要資訊在 github 上

### 關於測試

概念上可以分成兩層，一層是 `fetcher, parser 相關`，一層是 `flow, save 相關`  
這樣應該就涵蓋了所有的處理邏輯、流程，在細一些的如 utils、storage 的 unit test 因為涵蓋在此了就不各別測試了 

- `test_fetcher.py` mock 掉 request，主要測試資料整理的邏輯以及錯誤處理
- `test_action.py` 驗證完整流程是否有問題

### 關於部屬

想了幾種作法：

1. 將檔案拷貝至遠端機器且執行
2. 在遠端機器直接使用 git 抓取程式來執行
3. 包成 image 在遠端執行 run container

由於小專案的關係，就直接使用 fabric 來實作 `1` 了。  
優點就較為輕量，且直接寫 python 就能處理完，若是較複雜專案或是需要較多部屬的管理，那可能用 Ansible 會合適些。

不過這樣的方式多少還是有些隱憂，像是為了能執行遠端操作而開放的一些權限，或是說環境的管理 (package 安裝等等的)。像這次的實作就是先假設環境已經準備好，但若是遇到 package 需要調整就會是個問題。或許都還是可以透過一些 script 去調整，但個人會覺得做起來麻煩些就是。

相較起來 `3` 的方式我是較喜歡的，在 build image 時就可避免上面提到的隱憂，版本控管也相對再單純些。這邊沒實作是想說 demo 用 `1` 較單純好理解，run container 得要看整體環境來決定怎呈現

`2` 的話還要多開一個 git 權限，雖然簡單明瞭，但就抖抖的


### 關於排程

依照展品架構/需求，可能有幾種實作：

1. cronjob
2. FaaS 的排程功能 (如 AWS lambda 的排程)
3. 自行架設 Airflow
4. Django + 相關套件 (Celery / django-q)
5. 自行實作

這邊使用 `1` 較為單純，但管理上可能略為不便，規模較大時可以考慮其他方案。  

`2` 的部分要考量的是會不會有搬遷的需求，像是 AWS 搬到 GCP，或是入境中國得用騰訊、阿里之類的。有時太依賴平台功能會造成搬遷不易。

`3`~`5` 都算自己做的一種吧，還是得依照需求以及時間來評估

## 其他問題

- 本想使用 threading / asyncio 等作法來增快效率，不過有遇到 TWSE 的 request limit (據說是每 5 秒鐘 3 個 request)，超過 ip 會被 ban 掉，所以最後反而還加上了 sleep 來避免
- TWSE 的 exchange report 在某些情況下會回傳 `本公司全球資訊網已於106年5月23日改版` 這樣的頁面資訊，並不是回傳 json，所以會造成解析失敗，原因不太清楚，有可能跟 request limit 有關。不過已經加上了 sleep 以及 retry 的情況下還是沒辦法完全避開，造成有些個股資訊會無法取得，目前是以錯誤處理的方式來讓程式可以繼續執行完畢。
  - 或許可以使用 proxy 來避免，不過手上沒有資源就沒嘗試了
- TWSE 的 exchange report 有機會有 `['111/05/23', '0', '0', '--', '--', '--', '--', ' 0.00', '0']` 這樣的資料，目前是將其 diff 算為 0 來處理
