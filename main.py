import yt_dlp
from pydub import AudioSegment
import stable_whisper
import os
import ffmpeg
from moviepy.video.io.VideoFileClip import VideoFileClip

def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split('.'))
    return h * 3600 + m * 60 + s

# 사용자 입력 받기
youtube_url = input("유튜브 링크를 입력하세요: ")
start_time_str = input("시작 시간을 h.m.s 형식으로 입력하세요: ")
end_time_str = input("종료 시간을 h.m.s 형식으로 입력하세요: ")

# 시작 시간과 종료 시간을 초 단위로 변환
start_time = time_to_seconds(start_time_str)
end_time = time_to_seconds(end_time_str)
print("시작 시간: ", start_time)
print("종료 시간: ", end_time)

# 유튜브 영상 다운로드
print("다운로드 중...")
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'downloaded_video.%(ext)s',
    'merge_output_format': 'mp4',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([youtube_url])


# 다운로드한 영상 파일 자르기
print("영상 자르는 중...")
with VideoFileClip("downloaded_video.mp4") as video:
    new = video.subclip(start_time, end_time)
    new.write_videofile("trimmed_video.mp4")

# 오디오 파일 추출
print("오디오 추출 중...")
audio = AudioSegment.from_file("trimmed_video.mp4", format="mp4")
audio.export("trimmed_audio.mp3", format="mp3")

# Whisper 모델 로드
model = stable_whisper.load_model("large-v3")


# 오디오 텍스트 변환
print("오디오 텍스트 변환 중...")
result = model.transcribe("trimmed_audio.mp3", regroup=True, suppress_silence=True)
result = model.refine("trimmed_video.mp4", result)

# 텍스트 srt파일로 저장
print("텍스트를 srt파일로 변환 중...")
result.to_srt_vtt("original_subtitles.srt", tag=None, segment_level=True, word_level=False)