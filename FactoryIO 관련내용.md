# [FactoryIO] 실습0 (준비 및 설정)

![alt text](image-27.png)

![alt text](image-28.png)

![alt text](image-29.png)

![alt text](image-30.png)

#FactoryIO #실습 #설정 #시뮬레이션


# [FactoryIO] 실습1 (옵션설정)


<video src="/attachments/card-1783301498161/f1.mp4" controls playsinline autoplay muted loop width="100%"></video>

- Emmiter 옵션 (생성관여)
![alt text](image-31.png)


![alt text](image-32.png)


- 박스의 위치도 랜덤하게
![alt text](image-33.png)

#FactoryIO #실습 #옵션설정 #Emmiter #랜덤

# [FactoryIO] 실습2 (센서설정, 종류)

<video src="/attachments/card-1783305350690/f2.mp4" controls playsinline autoplay muted loop width="100%">
</video>

- Retroreflective sensor

![alt text](image-34.png)

>Retroreflective sensor(레트로리플렉티브 센서)
발광부와 수광부가 한 몸체에 들어 있고, 맞은편에 설치된 반사판(레트로리플렉터)을 이용해 빛을 되돌려 받는 방식으로 물체를 감지하는 광센서.
 물체가 센서와 반사판 사이를 지나 빛을 차단하면 출력 신호가 발생. 설치가 간단하고 감지 거리가 길어 산업 자동화에 널리 쓰임.



🔎 동작 원리

발광부(Emitter): LED 또는 레이저 다이오드가 특정 주파수로 변조된 빛(적외선, 가시광선)을 방출.

반사판(Retroreflector): 코너 큐브 프리즘이나 반사 테이프가 빛을 원래 방향으로 정확히 되돌려 줌.

수광부(Receiver): 되돌아온 빛을 감지. 물체가 빛을 차단하면 수광 신호가 급격히 줄어들어 센서 출력이 전환됨.

- 반사판이 없을 때
![alt text](image-35.png)

- 반사판 연결 초록불
![alt text](image-36.png)
![alt text](image-37.png)

#FactoryIO #레트로리플렉티브센서 #광센서 #산업자동화 #센서설정

# [FactoryIO] 실습3 (버튼설정, 종류)

<video src="/attachments/card-1783307854396/f3.mp4" controls playsinline autoplay muted loop width="100%"></video>

### 버튼류
- Normal Open - NO
평소에 0... 누르면 1  

- Normal Close - NC
평소에 1... 누르면 0  

- 주로 Emergency Button 류는 NC이다.

#FactoryIO #버튼 #NC #NO

# [FactoryIO] 실습4 (모드버스설정, 연동)

![image](/attachments/card-1783315754396/paste_1783315857267_99pda.png)

(디지털)읽기전용
10001 , 10002 ....
Descrete inputs : 입력(상태를 본다?, 상태를 읽어온다)

(디지털)읽기, 쓰기용
00001, 00002, 00003....
coils  : 출력

(아날로그)읽기전용
30001, 30002 ....
Input Registers

(아날로그)읽기, 쓰기용
40001, 40002 ....
Holding Registers
---
[[FA] docker-compose 로 모드버스 실습 컨테이너 실습1](./README.md)
[[FA] docker-compose 로 모드버스 실습 컨테이너 실습2](./README.md)
[[FA] docker-compose 로 모드버스 실습 컨테이너 실습3](./README.md)

![alt text](image-44.png)
![alt text](image-41.png)

- 주의점
![alt text](image-42.png)

연결모드가 Nofailure 

![alt text](image-43.png)

이 모양이 되어있어야 한다.

#FactoryIO #모드버스 #연동 #디지털 #아날로그

# [FactoryIO] 실습7 (Py으로 단계별 제어)

1)스캔방식으로 첫번째 센서 값 읽어오기
![alt text](image-45.png)

>Diffuse 센서는 빛을 물체에 쏘아 반사된 빛을 감지해 물체의 존재를 판별하는 광센서 (NO 방식)
![alt text](image-46.png)

```py
import pymodbus
import time as tt
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('210.119.14.56', port=502)
for n in range(10000):
    result = client.read_discrete_inputs(0, count=8, device_id=1) # 옛 slave, unit_id
    print(f"\r{result.bits}",end="")
    tt.sleep(0.1)
print("스캔종료")
```

2) 스토퍼 추가하기
![alt text](image-47.png)

```py
import time as tt
# 컨베어, 이미터, 리무버  켜기
client.write_coil(0, 1)
client.write_coil(6, 1)
client.write_coil(7, 1)
for n in range(10000):
    sensor = client.read_discrete_inputs(0, count=8, device_id=1).bits[0] # 옛 slave, unit_id
    print(f"\r{sensor}",end="")

    if sensor:
        client.write_coil(1, 1) # 스토퍼 ON
        tt.sleep(3)
        client.write_coil(1, 0)
        tt.sleep(3)
    else:
        client.write_coil(1, 0) # 스토퍼 OFF
    
    tt.sleep(0.1)
print("스캔종료") 
```

3) 푸셔 추가하기

![alt text](image-48.png)

#FactoryIO #ModbusTCP #Python #단계별제어

# [Factory IO] 파일저장/복구 위치

![alt text](image-49.png)

>C:\Users\ `자기계정` \Documents\Factory IO\My Scenes

# [PY] pymdbus 메소드
![alt text](image-50.png)

#pymdbus #python #dbus #메소드

# [FactoryIO] 디지털트윈 / 스마트팩토리 원격제어

![alt text](image-51.png)

![alt text](image-52.png)

# [FactoryIO] 실습8 (물류,이송,분류)

<video src="/attachments/card-1783487187856/f7.mp4" controls playsinline autoplay muted loop width="100%"></video>

``

센서 :
- 위치가 안맞을 경우
![alt text](image-53.png)
- 리시버에 맞을 경우 (초록LED)
![alt text](image-54.png)


```py
# 모드버스접속
from pymodbus.client import ModbusTcpClient
import time as tt
import threading
client = ModbusTcpClient('210.119.14.56', port=502)
client.connect()
# 초기화
client.write_coils(0, [0]*16 )
# 켜야되는 출력 8부터 8개 모두 On
client.write_coils(8, [1]*8 )
# 센서의 값 가지고 오기
sensor_scan = True
step = [0,0]

def sscan():
    while sensor_scan:
        ir = client.read_input_registers(0, count=8 ).registers[0]
        front_limit = client.read_discrete_inputs(0,count=8).bits[3]
        if ir == 224:
            client.write_coil(3,1)
            step[0] = 0
        if step[0] == 0 and (ir == 192 or ir == 128):
            client.write_coil(3,1) # 턴테이블 +이동
            step[0] = 1   
        if step[0] == 1 and front_limit:                                      
            client.write_coil(3,0) # 턴테이블 +정지
            client.write_coil(0,1) # 스토퍼 on
            client.write_coil(2,1) # 턴테이블 터닝 on
            step[1] = 1
        if step[1] == 1 and client.read_discrete_inputs(0,count=8).bits[1]: # 턴테이블이 돌았는지
            client.write_coil(2,1)
            client.write_coil(3,1)
            tt.sleep(3)
            client.write_coil(2,0)
            client.write_coil(0,0)
            step[0] = 0
            step[1] = 0

        tt.sleep(0.1)

thread_scan = threading.Thread(target=sscan, daemon=True)
print("센서로드 쓰레드 시작")
thread_scan.start()
```

#FactoryIO #물류 #자동화 #센서 #모드버스

# [FactoryIO] 실습9 (불량 분류)

- 이미터 세팅
![alt text](image-55.png)

- 비전카메라 세팅
![alt text](image-56.png)

- Modbus IO 세팅
![alt text](image-57.png)

```py
# 방법 1 sleep 을 사용 안하기
# 센서의 값 가지고 오기
scan_run = True
mem = [0]
def vscan():
    while scan_run:
       bits = client.read_discrete_inputs(0, count=8).bits
       if bits[0]:
        if mem[0] == 0:
            mem[0] = tt.monotonic()
        elif tt.monotonic() - mem[0] >= 1:
            client.write_coil(0,1) # Pusher On
            mem[0] = 0
       if bits[4]: 
        client.write_coil(0,0) # Pusher Off
        mem[0] = 0
        tt.sleep(0.1)
thread_vscan = threading.Thread(target=vscan, daemon=True)
print("센서로드 쓰레드 시작")
thread_vscan.start()
```

#FactoryIO #불량분류 #비전카메라 #Modbus #Python

# [FactoryIO] 실습10 작업중
![alt text](image-58.png)
![alt text](image-59.png)

> **📓 ipynb 분석 요약** (pyfa03_a(완).ipynb)

- **주제/목적**: FactoryIO 환경에서 Modbus TCP 통신을 통해 여러 공정(Vscan 클래스)을 제어하고 모니터링하는 예제입니다.

- **주요 흐름**:
    - Modbus TCP 클라이언트를 초기화하고 FactoryIO 서버에 연결합니다.
    - 모든 출력 코일을 초기화하여 Off 상태로 만듭니다.
    - 특정 출력 코일(2번부터 7개)을 On 상태로 설정합니다.
    - `Vscan` 클래스를 정의하여 각 공정의 센서 입력(`bit1`, `bit2`)을 읽고, 특정 조건(1초 동안 `bit1`이 On 상태 유지)에 따라 출력 코일(`coil`)을 제어합니다.
    - 두 개의 `Vscan` 객체(`vscan1`, `vscan2`)를 생성하고 각각의 센서와 제어 코일을 설정하여 스레드로 실행합니다.

- **사용 기술**:
    - `pymodbus`: Modbus TCP 통신 라이브러리
    - `threading`: 비동기 공정 처리를 위한 스레드 사용
    - `time`: 시간 관련 함수 (타이머 기능)

- **결과/결론**:
    - Modbus 서버와의 연결이 성공적으로 이루어집니다.
    - 출력 코일 제어가 가능하며, `Vscan` 클래스를 통해 정의된 두 개의 공정이 독립적인 스레드로 실행되어 FactoryIO 환경의 센서 상태에 따라 제어 코일을 on/off 합니다.

---

클래스로 처리
```py
# 클래스로 2공정 묶기

class Vscan:
    def __init__(self, client, bit1, bit2, coil):
        self.client = client
        self.scan_run = True
        self.bit1 = bit1
        self.bit2 = bit2
        self.coil = coil
        self.mem = 0

    def run(self):
        while self.scan_run:
            bits = self.client.read_discrete_inputs(0, count=8).bits
            if bits[self.bit1]:
                if self.mem == 0:
                    self.mem = tt.monotonic()
                elif tt.monotonic() - self.mem >= 1:
                    self.client.write_coil(self.coil,1) # Pusher On
                    self.mem = 0
            else:
                self.mem = 0  
            if bits[self.bit2]: 
                self.client.write_coil(self.coil,0) # Pusher Off
                self.mem = 0
            tt.sleep(0.1)

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        print("쓰레드 시작")
    def stop(self):
        self.scan_run = False
vscan1 = Vscan(client, 0, 3, 0)
vscan2 = Vscan(client, 1, 5, 1)
vscan1.start()
vscan2.start()
```

#FactoryIO #ModbusTCP #pymodbus #Vscan #threading

# [FactoryIO] 실습11 (원격다중접속제어)

> **📓 ipynb 분석 요약** (pyfa04(ing).ipynb)

- **주제/목적**: Factory IO와 Modbus TCP를 이용하여 데이터센터 냉각수 시스템의 밸브를 제어하고 수위를 모니터링하는 파이썬 노트북입니다.

- **주요 흐름**:
    - Modbus TCP 클라이언트를 생성하고 Factory IO 서버에 연결합니다.
    - Fill Valve와 Discharge Valve의 아날로그 출력을 제어합니다.
    - 여러 레지스터를 동시에 읽고 씁니다.
    - 아날로그 입력을 주기적으로 읽어와 현재 수위와 배수량을 모니터링합니다.
    - 수위 값에 따라 밸브 출력을 자동으로 조절하는 로직을 구현합니다.
    - 모니터링 스레드를 시작하고 중지합니다.

- **사용 기술**:
    - `pymodbus.client.ModbusTcpClient`: Modbus TCP 통신 클라이언트
    - `time` 라이브러리 (`tt` 별칭): 시간 지연
    - `threading` 라이브러리: 비동기 모니터링 스레드

- **결과/결론**:
    - Modbus TCP를 통해 Factory IO의 밸브를 성공적으로 연결하고 제어할 수 있습니다.
    - 실시간으로 수위 및 배수량 데이터를 읽어와 표시합니다.
    - 수위 변화에 따라 Fill Valve의 출력이 자동으로 조절되는 것을 확인할 수 있습니다.
    - 모니터링 스레드를 통해 시스템 상태를 실시간으로 감시할 수 있습니다.

---

![alt text](image-62.png)

#FactoryIO #ModbusTCP #Python #자동화 #제어시스템

# [FactoryIO] 실습12 (무게측정, 스케일 + 펄스기법, csv저장)

![alt text](image-63.png)

![alt text](image-64.png)

![alt text](image-65.png)

![alt text](image-66.png)

- 중요점:
>`전역변수설정` 
> state = {"prev": False} ,
> `상승 에지(0 → 1) 검출기법`
> if sensor and not state["prev"]:

- `csv 저장 및 시각화`
![alt text](image-67.png)

> **📓 ipynb 분석 요약** (pyfa05(완).ipynb)

## 주제/목적
Modbus TCP 통신을 사용하여 센서 값을 읽고, 특정 조건에서 무게 데이터를 로깅하며, 로깅된 데이터를 시각화

## 주요 흐름
*   Modbus TCP 클라이언트 초기화 및 연결.
*   초기 출력 코일 설정.
*   센서 값 변화(상승 에지) 감지 시 무게 데이터 읽기 및 CSV 파일에 로깅.
*   로깅된 데이터 중 최신 20개 데이터를 그래프로 시각화.

## 사용 기술
*   `pymodbus`: Modbus TCP 통신 클라이언트 구현.
*   `threading`: 센서 스캔을 백그라운드에서 실행.
*   `csv`: 센서 데이터를 CSV 파일로 저장.
*   `pandas`: CSV 파일 데이터를 DataFrame으로 로드.
*   `matplotlib.pyplot`: 로깅된 무게 데이터를 그래프로 시각화.

## 결과/결론
*   Modbus TCP 연결 성공 여부 (True).
*   코일 쓰기 응답 메시지.
*   센서 입력에 따라 무게(kg) 값을 실시간으로 콘솔에 출력하고 CSV 파일(`work/weight_log.csv`)에 기록.
*   최신 20개 무게 데이터를 시각화한 그래프 출력.

---

#FactoryIO #PLC #펄스 #자동화 #CSV저장 #시각화

