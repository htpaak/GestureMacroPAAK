import os
import sys
import logging

class TeeStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, message):
        for stream in self.streams:
            stream.write(message)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()

def setup_logging():
    # logs 디렉토리 생성
    os.makedirs("logs", exist_ok=True)
    log_file_path = os.path.abspath("logs/debug.log")

    # 로그 파일 열기 (덮어쓰기)
    log_file = open(log_file_path, mode='w', encoding='utf-8')

    # stdout, stderr 를 TeeStream으로 교체 (터미널 + 파일 모두 출력)
    sys.stdout = TeeStream(sys.__stdout__, log_file)
    sys.stderr = TeeStream(sys.__stderr__, log_file)

    # logging 설정
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout  # stdout도 이미 TeeStream이므로 파일+터미널로 감
    )

    logging.debug("Logging initialized.")
