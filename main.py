import os
import json
import asyncio
import threading
import random
import datetime
import customtkinter as ctk
from tkinter import messagebox
from playwright.async_api import async_playwright

# GUI 테마 및 색상 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TelegramAutoBot:
    """텔레그램 자동화 로직 및 데이터 관리를 담당하는 클래스"""
    def __init__(self):
        self.config_file = "telegram_config.json"
        self.is_running = False
        self.loop = None
        self.data = self.load_config()

    def load_config(self):
        """로컬 JSON 파일에서 설정 정보를 불러옵니다."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"original_message": "", "channels": []}

    def save_config(self):
        """현재 설정을 JSON 파일로 저장합니다."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    async def human_type(self, element, text):
        """사람이 타이핑하는 것처럼 글자 사이에 무작위 지연을 주어 입력합니다."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for char in line:
                # 글자당 0.05초 ~ 0.15초 사이의 무작위 지연
                await element.type(char, delay=random.uniform(50, 150))
            if i < len(lines) - 1:
                # 줄바꿈: Shift + Enter
                await element.press("Shift+Enter")
            else:
                # 마지막 줄: Enter로 전송
                await element.press("Enter")
        await asyncio.sleep(random.uniform(0.5, 1.0))

class App(ctk.CTk):
    """CustomTkinter 기반의 메인 GUI 클래스"""
    def __init__(self):
        super().__init__()
        self.bot = TelegramAutoBot()
        
        self.title("Telegram Auto Marketer (No-Spinning Version)")
        self.geometry("1100x750")

        # 그리드 레이아웃 설정
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 상단: 메시지 설정 영역 ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.top_frame, text="홍보 메시지 설정", font=("Apple SD Gothic Neo", 16, "bold")).pack(pady=5)
        self.msg_text = ctk.CTkTextbox(self.top_frame, height=120, width=900)
        self.msg_text.insert("1.0", self.bot.data["original_message"])
        self.msg_text.pack(padx=20, pady=10)
        
        self.save_msg_btn = ctk.CTkButton(self.top_frame, text="메시지 저장", command=self.save_message)
        self.save_msg_btn.pack(pady=5)

        # --- 좌측: 채널 관리 패널 ---
        self.left_panel = ctk.CTkFrame(self, width=320)
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        
        ctk.CTkLabel(self.left_panel, text="채널 리스트 관리", font=("Apple SD Gothic Neo", 15, "bold")).pack(pady=15)
        
        self.ch_name = ctk.CTkEntry(self.left_panel, placeholder_text="채널 별칭 (예: 홍보방1)")
        self.ch_name.pack(padx=20, pady=5, fill="x")
        self.ch_url = ctk.CTkEntry(self.left_panel, placeholder_text="텔레그램 Web URL")
        self.ch_url.pack(padx=20, pady=5, fill="x")
        self.ch_cool = ctk.CTkEntry(self.left_panel, placeholder_text="쿨타임 (분 단위 숫자)")
        self.ch_cool.pack(padx=20, pady=5, fill="x")
        
        self.add_btn = ctk.CTkButton(self.left_panel, text="채널 추가", command=self.add_channel)
        self.add_btn.pack(padx=20, pady=15, fill="x")
        
        self.channel_list_box = ctk.CTkOptionMenu(self.left_panel, values=self.get_channel_names())
        self.channel_list_box.pack(padx=20, pady=5, fill="x")
        
        self.del_btn = ctk.CTkButton(self.left_panel, text="선택 채널 삭제", fg_color="#E74C3C", hover_color="#C0392B", command=self.delete_channel)
        self.del_btn.pack(padx=20, pady=5, fill="x")

        # --- 우측: 실행 상태 및 로그 패널 ---
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        
        self.control_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.control_frame.pack(pady=15)
        
        self.start_btn = ctk.CTkButton(self.control_frame, text="자동 홍보 시작", fg_color="#27AE60", hover_color="#1E8449", width=150, height=40, command=self.start_bot)
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(self.control_frame, text="자동 홍보 중지", fg_color="#7F8C8D", state="disabled", width=150, height=40, command=self.stop_bot)
        self.stop_btn.pack(side="left", padx=10)
        
        self.log_view = ctk.CTkTextbox(self.right_panel, fg_color="#1C1C1C", text_color="#00FF41", font=("Courier New", 13))
        self.log_view.pack(padx=15, pady=15, fill="both", expand=True)

    def get_channel_names(self):
        """현재 저장된 채널 이름 목록을 반환합니다."""
        names = [c["name"] for c in self.bot.data["channels"]]
        return names if names else ["등록된 채널 없음"]

    def log(self, message):
        """로그 창에 시간과 함께 메시지를 출력합니다 (Thread-safe)."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_view.insert("end", f"[{timestamp}] {message}\n")
        self.log_view.see("end")

    def save_message(self):
        """입력된 홍보 메시지를 저장합니다."""
        self.bot.data["original_message"] = self.msg_text.get("1.0", "end-1c")
        self.bot.save_config()
        messagebox.showinfo("저장 완료", "홍보 메시지가 로컬에 저장되었습니다.")

    def add_channel(self):
        """새로운 홍보 채널을 리스트에 추가합니다."""
        name = self.ch_name.get()
        url = self.ch_url.get()
        cool = self.ch_cool.get()
        
        if not name or not url or not cool:
            messagebox.showwarning("입력 오류", "모든 정보를 입력해주세요.")
            return
        
        try:
            cool_val = int(cool)
        except ValueError:
            messagebox.showwarning("입력 오류", "쿨타임은 숫자만 입력 가능합니다.")
            return

        self.bot.data["channels"].append({
            "name": name,
            "url": url,
            "cooldown": cool_val,
            "last_post": None
        })
        self.bot.save_config()
        self.channel_list_box.configure(values=self.get_channel_names())
        self.log(f"새 채널 추가됨: {name}")
        self.ch_name.delete(0, "end"); self.ch_url.delete(0, "end"); self.ch_cool.delete(0, "end")

    def delete_channel(self):
        """선택된 채널을 삭제합니다."""
        selected = self.channel_list_box.get()
        if selected == "등록된 채널 없음": return
        
        self.bot.data["channels"] = [c for c in self.bot.data["channels"] if c["name"] != selected]
        self.bot.save_config()
        self.channel_list_box.configure(values=self.get_channel_names())
        self.log(f"채널 삭제됨: {selected}")

    def start_bot(self):
        """자동화 스레드를 시작합니다."""
        if not self.bot.data["original_message"].strip():
            messagebox.showwarning("경고", "홍보 메시지를 먼저 입력하고 저장하세요.")
            return
        
        self.bot.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", fg_color="#C0392B")
        self.log(">>> 자동 홍보 프로세스를 시작합니다.")
        
        # GUI 프리징 방지를 위해 별도 스레드에서 실행
        threading.Thread(target=self.run_async_loop, daemon=True).start()

    def stop_bot(self):
        """자동화 프로세스를 중지합니다."""
        self.bot.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled", fg_color="#7F8C8D")
        self.log("<<< 중지 명령이 수신되었습니다. 현재 작업 후 종료됩니다.")

    def run_async_loop(self):
        """비동기 이벤트 루프 생성 및 실행"""
        self.bot.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.bot.loop)
        self.bot.loop.run_until_complete(self.automation_worker())

    async def automation_worker(self):
        """Playwright 기반의 실제 자동화 작업 루프"""
        async with async_playwright() as p:
            page = None
            browser = None
            cdp_connected = False
            
            try:
                # 기존 텔레그램 앱 브라우저에 연결 시도 (디버깅 포트 9222 사용)
                browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                cdp_connected = True
                self.log("기존 텔레그램 브라우저에 연결되었습니다.")
                
                # 기존 컨텍스트와 페이지를 사용
                contexts = browser.contexts
                if not contexts:
                    raise Exception("텔레그램 브라우저에 컨텍스트가 없습니다.")
                
                context = contexts[0]
                pages = context.pages
                if not pages:
                    raise Exception("텔레그램 브라우저에 페이지가 없습니다.")
                
                # 텔레그램 웹 페이지 찾기 (URL에 'web.telegram.org' 포함)
                for p in pages:
                    if "web.telegram.org" in p.url:
                        page = p
                        break
                
                if not page:
                    raise Exception("텔레그램 웹 페이지를 찾을 수 없습니다. 텔레그램 웹이 열려 있는지 확인하세요.")
                
                self.log("텔레그램 웹 페이지에 연결되었습니다. 자동화 시작.")
                
            except Exception as e:
                self.log(f"기존 브라우저 연결 실패: {str(e)}")
                self.log("새 브라우저를 열어 텔레그램 웹에 연결합니다.")
                
                # Fallback: 새로운 브라우저 실행
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                
                # 텔레그램 웹으로 이동
                await page.goto("https://web.telegram.org/")
                self.log("새 브라우저가 실행되었습니다. 텔레그램 웹에 로그인해주세요.")
                
                # 로그인 대기 (수동)
                await asyncio.sleep(10)  # 사용자가 로그인할 시간 제공
            
            while self.bot.is_running:
                now = datetime.datetime.now()
                self.log(f"[정보] 채널 검사 시작 (총 {len(self.bot.data['channels'])}개 채널)")
                
                for idx, channel in enumerate(self.bot.data["channels"], 1):
                    if not self.bot.is_running: break
                    self.log(f"[{idx}/{len(self.bot.data['channels'])}] {channel['name']} 채널 처리 중...")
                    
                    # 쿨타임 체크 로직
                    should_post = False
                    last_post_str = channel.get("last_post")
                    
                    if last_post_str is None:
                        should_post = True
                        self.log(f"[{channel['name']}] 쿨타임 없음 - 포스팅 가능")
                    else:
                        last_time = datetime.datetime.fromisoformat(last_post_str)
                        elapsed = (now - last_time).total_seconds() / 60
                        self.log(f"[{channel['name']}] 마지막 포스팅: {last_post_str}, 경과시간: {elapsed:.1f}분, 쿨타임: {channel['cooldown']}분")
                        if elapsed >= channel["cooldown"]:
                            should_post = True
                            self.log(f"[{channel['name']}] 쿨타임 완료 - 포스팅 가능")
                        else:
                            self.log(f"[{channel['name']}] 쿨타임 대기 중 (남은 시간: {channel['cooldown'] - elapsed:.1f}분)")
                    
                    if not should_post:
                        continue
                    
                    self.log(f"[{channel['name']}] 진입 중: {channel['url']}")
                    
                    try:
                        # URL 변환: 다양한 형식의 채널 주소를 web.telegram.org로 변환
                        channel_url = channel["url"].strip()
                        
                        # 형식 1: @username 형식
                        if channel_url.startswith("@"):
                            username = channel_url[1:]  # @ 제거
                            channel_url = f"https://web.telegram.org/k/#@{username}"
                        # 형식 2: username 형식 (@ 없음, URL도 아님)
                        elif not channel_url.startswith("https://") and "@" not in channel_url:
                            channel_url = f"https://web.telegram.org/k/#@{channel_url}"
                        # 형식 3: https://t.me/ 형식
                        elif channel_url.startswith("https://t.me/"):
                            username = channel_url.replace("https://t.me/", "").split("/")[0]  # / 이후 제거
                            channel_url = f"https://web.telegram.org/k/#@{username}"
                        # 형식 4: 이미 https://web.telegram.org/ 형식
                        elif channel_url.startswith("https://web.telegram.org/"):
                            pass  # 그대로 사용
                        else:
                            self.log(f"[{channel['name']}] URL 형식이 올바르지 않습니다: {channel_url}")
                            continue
                        
                        # 1. 채널 URL 이동
                        self.log(f"[{channel['name']}] 채널로 이동 중...")
                        try:
                            await page.goto(channel_url, timeout=60000)  # 60초 타임아웃
                            self.log(f"[{channel['name']}] 페이지 이동 성공")
                        except Exception as goto_error:
                            self.log(f"[{channel['name']}] 페이지 이동 실패: {str(goto_error)}")
                            raise Exception(f"페이지 이동 실패: {str(goto_error)}")
                        
                        # 페이지 로드 대기 (더 짧은 타임아웃으로 변경)
                        try:
                            await page.wait_for_load_state('domcontentloaded', timeout=30000)
                            self.log(f"[{channel['name']}] DOM 로드 완료")
                        except Exception as load_error:
                            self.log(f"[{channel['name']}] 페이지 로드 대기 실패: {str(load_error)}")
                            # 로드 실패해도 계속 진행 (일부 페이지에서는 필요)
                        
                        await asyncio.sleep(2)  # 추가 안정화 대기
                        
                        # 채널 페이지가 제대로 로드되었는지 확인
                        current_url = page.url
                        self.log(f"[{channel['name']}] 현재 URL: {current_url}")
                        if "web.telegram.org" not in current_url:
                            raise Exception(f"채널 페이지 로드 실패: {current_url}")
                        
                        self.log(f"[{channel['name']}] 채널 페이지 로드 완료")
                        
                        # 2. 무작위 지터링 (사람처럼 보이기 위함)
                        jitter = random.randint(15, 45)
                        self.log(f"[{channel['name']}] 사람처럼 행동하기 위해 {jitter}초 대기...")
                        await asyncio.sleep(jitter)
                        
                        # 3. 입력창 찾기 및 타이핑
                        # 텔레그램 웹 버전에 따라 셀렉터가 다를 수 있음
                        self.log(f"[{channel['name']}] 입력창 찾는 중...")
                        input_selectors = [
                            "div.input-message-input",
                            "div[contenteditable='true']",
                            "textarea",
                            ".input-message-input"
                        ]
                        input_element = None
                        for selector in input_selectors:
                            try:
                                self.log(f"[{channel['name']}] {selector} 시도 중...")
                                input_element = await page.wait_for_selector(selector, timeout=15000)  # 15초로 증가
                                if input_element:
                                    self.log(f"[{channel['name']}] 입력창 발견: {selector}")
                                    break
                            except Exception as selector_error:
                                self.log(f"[{channel['name']}] {selector} 찾기 실패: {str(selector_error)}")
                                continue
                        
                        if not input_element:
                            # 입력창이 없으면 채널 권한이 없는 것일 수 있음
                            page_content = await page.content()
                            if "You can only post messages as admin" in page_content or "관리자만" in page_content:
                                raise Exception("채널 관리자 권한이 필요합니다.")
                            elif "channel" in page_content.lower() and "not found" in page_content.lower():
                                raise Exception("채널을 찾을 수 없습니다.")
                            else:
                                raise Exception("입력창을 찾을 수 없습니다.")
                        
                        msg = self.bot.data["original_message"]
                        self.log(f"[{channel['name']}] 메시지 입력 시작...")
                        await self.bot.human_type(input_element, msg)
                        self.log(f"[{channel['name']}] 메시지 전송 완료")
                        
                        # 4. 결과 기록
                        channel["last_post"] = datetime.datetime.now().isoformat()
                        self.bot.save_config()
                        self.log(f"[{channel['name']}] 포스팅 완료 성공!")
                        
                        # 다음 채널 처리 전 채널 전환 안정화 대기
                        if idx < len(self.bot.data["channels"]):
                            self.log(f"다음 채널로 전환 준비 중...")
                            await asyncio.sleep(5)  # 채널 간 전환 대기
                        
                    except Exception as e:
                        self.log(f"[{channel['name']}] 오류 발생: {str(e)}")
                        # 실패 시 다음 주기에 다시 시도하도록 last_post를 업데이트하지 않음
                
                if self.bot.is_running:
                    self.log("모든 채널 검사 완료. 1분 후 다시 확인합니다.")
                    await asyncio.sleep(60)

            # CDP 연결이 아니면 브라우저 닫기
            if not cdp_connected and browser:
                await browser.close()
            self.log("자동화 세션이 종료되었습니다.")

if __name__ == "__main__":
    app = App()
    app.mainloop()