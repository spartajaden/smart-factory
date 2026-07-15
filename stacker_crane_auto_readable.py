"""Factory I/O Stacker Crane — 자동 입출고 사이클 (pymodbus 3.13+)

Factory I/O Numerical Stacker Crane 프로토콜:
  - 랙 셀(1~54): register 0 → 0 → register 0 → position
  - 복귀(55):     register 0 → 55
"""

from __future__ import annotations

import time
from typing import Any

from pymodbus.client import ModbusTcpClient


# ============================================================================
# 1. Modbus 연결 설정
# ============================================================================

HOST = "210.119.14.58"
PORT = 502
DEVICE_ID = 1

TIMEOUT_SECONDS = 10.0
TRAVEL_SECONDS = {
    "per_slot": 0.23,
    "base": 1.5,
    "min": 2.0,
    "rest": 10.0,
}

POLL_SECONDS = 0.05
TRANSFER_SECONDS = 1.0
OUTFEED_SECONDS = 3.0
EXIT_FEED_SECONDS = 2.0


# ============================================================================
# 2. Modbus 주소 매핑 (zero-based)
# ============================================================================

AT_LOAD = 0
AT_LEFT = 1
AT_RIGHT = 2
AT_MIDDLE = 3
MOVING_X = 4
MOVING_Z = 5

LOAD_CONVEYOR = 0
FORK_LEFT = 1
FORK_RIGHT = 2
LIFT = 3
UNLOAD_CONVEYOR = 4
EXIT_CONVEYOR = 5

TARGET_POSITION = 0
REST_POSITION = 55

MOTION_COILS = (
    LOAD_CONVEYOR,
    FORK_LEFT,
    FORK_RIGHT,
    LIFT,
    UNLOAD_CONVEYOR,
    EXIT_CONVEYOR,
)


# ============================================================================
# 3. 예외 클래스
# ============================================================================

class CraneError(RuntimeError):
    pass


# ============================================================================
# 4. Modbus 통신 헬퍼
# ============================================================================

def _require_ok(response: Any, operation: str) -> None:
    if response is None or response.isError():
        raise CraneError(f"Modbus {operation} 실패: {response}")


def _read_di(address: int) -> bool:
    response = client.read_discrete_inputs(address, count=1, device_id=DEVICE_ID)
    _require_ok(response, f"DI 읽기 address={address}")
    return bool(response.bits[0])


def _write_coil(address: int, value: bool) -> None:
    response = client.write_coil(address, value, device_id=DEVICE_ID)
    _require_ok(response, f"Coil 쓰기 address={address} value={value}")


def _write_register(address: int, value: int) -> None:
    if not 0 <= value <= 65535:
        raise ValueError(f"Register 값은 0~65535 사이여야 합니다. 입력값: {value}")

    response = client.write_register(address, value, device_id=DEVICE_ID)
    _require_ok(response, f"Register[{address}] = {value}")


def _read_target_register() -> int:
    response = client.read_holding_registers(TARGET_POSITION, count=1, device_id=DEVICE_ID)
    _require_ok(response, "Holding Register 읽기")
    return int(response.registers[0])


def _debug_state(label: str) -> None:
    print(
        f"[DEBUG] {label}: "
        f"AT_LOAD={_read_di(AT_LOAD)} AT_MIDDLE={_read_di(AT_MIDDLE)} "
        f"MOVING_X={_read_di(MOVING_X)} MOVING_Z={_read_di(MOVING_Z)} "
        f"TARGET={_read_target_register()}"
    )


def scan_all_discrete_inputs(start: int = 0, end: int = 15) -> None:
    print("--- DI 전체 스캔 시작 ---")
    for addr in range(start, end + 1):
        try:
            response = client.read_discrete_inputs(addr, count=1, device_id=DEVICE_ID)
            if response and not response.isError():
                print(f"DI[{addr}] = {response.bits[0]}")
            else:
                print(f"DI[{addr}] = ERR")
        except Exception as exc:
            print(f"DI[{addr}] 읽기 실패: {exc}")
    print("--- DI 전체 스캔 완료 ---")


# ============================================================================
# 5. 상태 대기 함수
# ============================================================================

def _wait_for_di(address: int, expected: bool, timeout: float, name: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _read_di(address) == expected:
            print(f"  ✓ {name}")
            return
        time.sleep(POLL_SECONDS)
    raise CraneError(f"타임아웃: {timeout:.1f}초 동안 {name} 대기 실패")


# ============================================================================
# 6. 안전 장치
# ============================================================================

def stop_all() -> None:
    for address in MOTION_COILS:
        try:
            _write_coil(address, False)
        except CraneError:
            pass


def _assert_fork_centered() -> None:
    if not _read_di(AT_MIDDLE):
        print(" ⚠ 포크가 중앙에 없음. 강제 정렬 중...")
        _write_coil(FORK_LEFT, False)
        _write_coil(FORK_RIGHT, False)
        _write_coil(LIFT, True)


# ============================================================================
# 7. 크레인 이동 (이동 확인용)
# ============================================================================

def _prepare_for_travel() -> None:
    _assert_fork_centered()
    _write_coil(FORK_LEFT, False)
    _write_coil(FORK_RIGHT, False)
    _write_coil(LIFT, True)
    time.sleep(TRANSFER_SECONDS)


def _travel_time(position: int) -> float:
    if position == REST_POSITION:
        return TRAVEL_SECONDS["rest"]
    return max(TRAVEL_SECONDS["min"], position * TRAVEL_SECONDS["per_slot"] + TRAVEL_SECONDS["base"])


def move_to(position: int) -> None:
    if not 1 <= position <= REST_POSITION:
        raise ValueError(f"목표 위치는 1~{REST_POSITION} 사이여야 합니다.")

    _prepare_for_travel()

    wait_time = _travel_time(position)
    print(f"\n▶ 이동 명령: target={position}, 예상 대기={wait_time:.1f}초")
    _debug_state("이동 전")

    _write_register(TARGET_POSITION, 0)
    time.sleep(0.2)
    _write_register(TARGET_POSITION, position)

    _debug_state("이동 명령 직후")
    time.sleep(0.5)
    _debug_state("0.5초 후")

    time.sleep(wait_time)
    _debug_state("예상 이동 후")
    print(f"  ✓ 목표 {position} 도착 완료")


# ============================================================================
# 8. 팔레트 핸들링
# ============================================================================

def pick_from_load() -> None:
    _write_coil(LOAD_CONVEYOR, True)
    _wait_for_di(AT_LOAD, True, TIMEOUT_SECONDS, "AT_LOAD")
    _write_coil(LOAD_CONVEYOR, False)
    _assert_fork_centered()
    _write_coil(LIFT, False)
    _write_coil(FORK_LEFT, True)
    _wait_for_di(AT_LEFT, True, TIMEOUT_SECONDS, "AT_LEFT")
    _write_coil(LIFT, True)
    time.sleep(TRANSFER_SECONDS)
    _write_coil(FORK_LEFT, False)
    _wait_for_di(AT_MIDDLE, True, TIMEOUT_SECONDS, "AT_MIDDLE")


def place_on_right() -> None:
    _assert_fork_centered()
    _write_coil(FORK_RIGHT, True)
    _wait_for_di(AT_RIGHT, True, TIMEOUT_SECONDS, "AT_RIGHT")
    _write_coil(LIFT, False)
    time.sleep(TRANSFER_SECONDS)
    _write_coil(FORK_RIGHT, False)
    _wait_for_di(AT_MIDDLE, True, TIMEOUT_SECONDS, "AT_MIDDLE")


def retrieve_from_right() -> None:
    _assert_fork_centered()
    _write_coil(LIFT, False)
    _write_coil(FORK_RIGHT, True)
    _wait_for_di(AT_RIGHT, True, TIMEOUT_SECONDS, "AT_RIGHT")
    _write_coil(LIFT, True)
    time.sleep(TRANSFER_SECONDS)
    _write_coil(FORK_RIGHT, False)
    _wait_for_di(AT_MIDDLE, True, TIMEOUT_SECONDS, "AT_MIDDLE")


def unload_to_left() -> None:
    _assert_fork_centered()
    _write_coil(FORK_LEFT, True)
    _wait_for_di(AT_LEFT, True, TIMEOUT_SECONDS, "AT_LEFT")
    _write_coil(LIFT, False)
    time.sleep(TRANSFER_SECONDS)
    _write_coil(FORK_LEFT, False)
    _wait_for_di(AT_MIDDLE, True, TIMEOUT_SECONDS, "AT_MIDDLE")

    print("  언로드 컨베이어 구동...")
    _write_coil(UNLOAD_CONVEYOR, True)
    time.sleep(OUTFEED_SECONDS)
    _write_coil(UNLOAD_CONVEYOR, False)

    print("  Exit 컨베이어 구동...")
    _write_coil(EXIT_CONVEYOR, True)
    time.sleep(EXIT_FEED_SECONDS)
    _write_coil(EXIT_CONVEYOR, False)


# ============================================================================
# 9. 고수준 사이클
# ============================================================================

def store(target: int) -> None:
    print(f"\n{'=' * 50}\n  Slot {target}: 입고 시작\n{'=' * 50}")
    pick_from_load()
    move_to(target)
    place_on_right()
    move_to(REST_POSITION)
    print(f"  Slot {target}: 입고 완료 ✅")


def retrieve(target: int) -> None:
    print(f"\n{'=' * 50}\n  Slot {target}: 출고 시작\n{'=' * 50}")
    move_to(target)
    retrieve_from_right()
    move_to(REST_POSITION)
    unload_to_left()
    print(f"  Slot {target}: 출고 완료 ✅")


def store_then_retrieve(target: int) -> None:
    store(target)
    retrieve(target)


# ============================================================================
# 10. 메인
# ============================================================================

def scan_all_discrete_inputs(start: int = 0, end: int = 15) -> None:
    print("--- DI 전체 스캔 시작 ---")
    for addr in range(start, end + 1):
        try:
            response = client.read_discrete_inputs(addr, count=1, device_id=DEVICE_ID)
            if response and not response.isError():
                print(f"DI[{addr}] = {response.bits[0]}")
            else:
                print(f"DI[{addr}] = ERR")
        except Exception as exc:
            print(f"DI[{addr}] 읽기 실패: {exc}")
    print("--- DI 전체 스캔 완료 ---")


def main() -> None:
    global client
    client = ModbusTcpClient(HOST, port=PORT, timeout=3)
    if not client.connect():
        raise ConnectionError(f"Factory I/O 연결 실패: {HOST}:{PORT}")

    print("Factory I/O 연결 성공.")
    print("--- 실시간 통신 확인 ---")
    res = client.read_discrete_inputs(4, count=1, device_id=DEVICE_ID)
    if res and not res.isError():
        print(f"DEBUG: 직접 읽은 Input 4의 값: {res.bits[0]}")
    else:
        print("DEBUG: 통신 자체가 안 됨!")

    try:
        stop_all()
        _assert_fork_centered()

        for slot in range(1, 2):
            try:
                store_then_retrieve(slot)
            except (CraneError, ConnectionError, ValueError) as err:
                print(f"  ❌ Slot {slot} 실패: {err}")
                try:
                    stop_all()
                    _write_register(TARGET_POSITION, REST_POSITION)
                    time.sleep(TRAVEL_SECONDS["rest"])
                except Exception:
                    pass
                continue

    except (KeyboardInterrupt, SystemExit):
        print("\n[🛑 중단]")

    finally:
        stop_all()
        client.close()
        print("종료.")


if __name__ == "__main__":
    main()
