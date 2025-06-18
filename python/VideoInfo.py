import pyautogui
import yt_dlp
import whisper
import psycopg2
from dataclasses import dataclass
from typing import Optional
import time
import os


@dataclass
class VideoInfo:
    url: str
    title: str
    uploader: str
    upload_date: str
    duration: float
    file_path: Optional[str] = None
    subtitle_path: Optional[str] = None


class BilibiliUIFinder:
    """使用pyautogui从B站界面获取最新视频链接"""

    def __init__(self, bilibili_url: str = "https://www.bilibili.com"):
        self.bilibili_url = bilibili_url

    def find_latest_video(self) -> Optional[VideoInfo]:
        """
        模拟用户操作获取最新视频
        返回VideoInfo对象或None
        """
        try:
            # 这里简化了实际UI操作，实际应用中需要更复杂的定位逻辑
            pyautogui.hotkey('ctrl', 't')
            pyautogui.typewrite(self.bilibili_url)
            pyautogui.press('enter')
            time.sleep(3)  # 等待页面加载

            # 假设最新视频在特定位置，实际需要根据UI调整
            pyautogui.click(x=100, y=200)  # 点击最新视频
            time.sleep(2)

            current_url = pyautogui.getActiveWindow().title
            if "bilibili.com/video/" not in current_url:
                return None

            # 获取视频信息 - 这里简化了，实际可能需要OCR或其他方法
            title = "从UI获取的视频标题"  # 需要实际实现获取逻辑
            return VideoInfo(
                url=current_url,
                title=title,
                uploader="从UI获取的UP主",
                upload_date=time.strftime("%Y%m%d"),
                duration=0.0
            )
        except Exception as e:
            print(f"UI操作失败: {e}")
            return None


class VideoDownloader:
    """使用yt-dlp下载视频"""

    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

    def download(self, video_info: VideoInfo) -> VideoInfo:
        """下载视频并返回更新后的VideoInfo"""
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_info.url, download=True)
                video_info.title = info_dict.get('title', video_info.title)
                video_info.uploader = info_dict.get('uploader', video_info.uploader)
                video_info.upload_date = info_dict.get('upload_date', video_info.upload_date)
                video_info.duration = info_dict.get('duration', video_info.duration)
                video_info.file_path = ydl.prepare_filename(info_dict)

            return video_info
        except Exception as e:
            print(f"下载失败: {e}")
            raise


class SubtitleGenerator:
    """使用Whisper生成字幕"""

    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)

    def generate_subtitle(self, video_info: VideoInfo) -> VideoInfo:
        """生成字幕并返回更新后的VideoInfo"""
        if not video_info.file_path:
            raise ValueError("没有可用的视频文件路径")

        try:
            result = self.model.transcribe(video_info.file_path)
            subtitle_path = os.path.splitext(video_info.file_path)[0] + ".srt"

            with open(subtitle_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"]):
                    f.write(f"{i + 1}\n")
                    f.write(f"{segment['start']} --> {segment['end']}\n")
                    f.write(f"{segment['text']}\n\n")

            video_info.subtitle_path = subtitle_path
            return video_info
        except Exception as e:
            print(f"字幕生成失败: {e}")
            raise


class VideoDatabase:
    """PostgreSQL数据库存储"""

    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self._create_table()

    def _create_table(self):
        """创建视频信息表"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    uploader TEXT NOT NULL,
                    upload_date DATE,
                    duration FLOAT,
                    file_path TEXT,
                    subtitle_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()

    def save_video_info(self, video_info: VideoInfo) -> bool:
        """保存视频信息到数据库"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO videos (url, title, uploader, upload_date, duration, file_path, subtitle_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        uploader = EXCLUDED.uploader,
                        file_path = EXCLUDED.file_path,
                        subtitle_path = EXCLUDED.subtitle_path
                """, (
                    video_info.url,
                    video_info.title,
                    video_info.uploader,
                    video_info.upload_date,
                    video_info.duration,
                    video_info.file_path,
                    video_info.subtitle_path
                ))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"数据库保存失败: {e}")
            self.conn.rollback()
            return False

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


class VideoPipeline:
    """视频处理管道，协调各个组件"""

    def __init__(self):
        self.ui_finder = BilibiliUIFinder()
        self.downloader = VideoDownloader()
        self.subtitle_gen = SubtitleGenerator()
        self.database = VideoDatabase(
            dbname="video_db",
            user="postgres",
            password="password"
        )

    def run(self):
        """运行整个流程"""
        try:
            # 1. 从UI获取视频信息
            video_info = self.ui_finder.find_latest_video()
            if not video_info:
                print("没有找到最新视频")
                return

            print(f"找到视频: {video_info.title}")

            # 2. 下载视频
            video_info = self.downloader.download(video_info)
            print(f"视频下载完成: {video_info.file_path}")

            # 3. 生成字幕
            video_info = self.subtitle_gen.generate_subtitle(video_info)
            print(f"字幕生成完成: {video_info.subtitle_path}")

            # 4. 存入数据库
            if self.database.save_video_info(video_info):
                print("视频信息已存入数据库")
            else:
                print("视频信息存入数据库失败")

        except Exception as e:
            print(f"处理流程出错: {e}")
        finally:
            self.database.close()


if __name__ == "__main__":
    pipeline = VideoPipeline()
    pipeline.run()