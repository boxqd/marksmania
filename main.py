'''MarksMania!! - A simple target shooting game using pygame and tkinter
This game features different types of targets, a scoring system, and a timer. 
Created by @boxqd (github.com/boxqd)'''

import tkinter as tk
from PIL import Image, ImageTk
import random
import pygame
import time

pygame.mixer.init()

TARGET_LIFETIME = 1500
TARGET_SIZE = 70
GAME_DURATION = 30000
VOLUME_FX = 0.8
VOLUME_BGM = 0.5

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
GROUND_SURFACE = 550

class MarksMania:
    def __init__(self, root):
        self.root = root
        self.root.title("MarksMania!!")

        # sounds
        self.snd_target_hit = pygame.mixer.Sound('sounds/target.mp3')
        self.snd_target_hit.set_volume(VOLUME_FX)
        self.snd_button_click = pygame.mixer.Sound('sounds/click.mp3')
        self.snd_button_click.set_volume(VOLUME_FX)
        self.snd_game_start = pygame.mixer.Sound('sounds/startgame.mp3')
        self.snd_game_start.set_volume(VOLUME_FX)

        self.POINTS = 0
        self.ACTIVE_TARGETS = {}
        self.IMAGE_REFERENCES = {}
        self.GAME_ACTIVE = False
        self.game_timer_id = None
        self.time_left = GAME_DURATION

        self.menu_frame = tk.Frame(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.pack()

        self.game_frame = tk.Frame(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.game_frame.pack_propagate(False)

        self.create_menu()

        self.canvas = tk.Canvas(self.game_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        self.score_label = tk.Label(self.game_frame, text=f"Score: {self.POINTS}", font=("Arial", 16))
        self.score_label.place(x=CANVAS_WIDTH - 10, y=CANVAS_HEIGHT - 10, anchor='se')

        self.timer_label = tk.Label(self.game_frame, text=self.format_time(self.time_left), font=("Arial", 16))
        self.timer_label.place(x=10, y=CANVAS_HEIGHT - 10, anchor='sw')

        self.endgame_frame = tk.Frame(self.game_frame)
        self.retry_button = tk.Button(self.endgame_frame, text="Retry", font=("Arial", 14), command=self.retry_game)
        self.quit_button = tk.Button(self.endgame_frame, text="Quit", font=("Arial", 14), command=self.root.destroy)
        self.retry_button.pack(side=tk.LEFT, padx=10)
        self.quit_button.pack(side=tk.LEFT, padx=10)

    def format_time(self, milliseconds):
        # formats ms to min:sec
        total_seconds = max(milliseconds // 1000, 0)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"Time: {minutes:01d}:{seconds:02d}"

    def create_menu(self):
        # menu stuff
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        self.menu_canvas = tk.Canvas(self.menu_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, highlightthickness=0, bd=0)
        self.menu_canvas.place(x=0, y=0)

        menubg_img = Image.open('images/menubg.png').resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)
        self.menu_bg_photo = ImageTk.PhotoImage(menubg_img)
        logo_img = Image.open('images/logo.png').resize((300, 120), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        self.btn_start_img = ImageTk.PhotoImage(Image.open('images/btn_start.png').resize((220, 60), Image.LANCZOS))
        self.btn_ins_img = ImageTk.PhotoImage(Image.open('images/btn_ins.png').resize((220, 60), Image.LANCZOS))
        self.btn_quit_img = ImageTk.PhotoImage(Image.open('images/btn_quit.png').resize((220, 60), Image.LANCZOS))

        self.menu_canvas.create_image(0, 0, anchor='nw', image=self.menu_bg_photo)
        self.menu_canvas.create_image(CANVAS_WIDTH//2, 100, anchor='n', image=self.logo_photo)
        start_btn = self.menu_canvas.create_image(CANVAS_WIDTH//2, 260, anchor='n', image=self.btn_start_img, tags="start_btn")
        ins_btn = self.menu_canvas.create_image(CANVAS_WIDTH//2, 340, anchor='n', image=self.btn_ins_img, tags="ins_btn")
        quit_btn = self.menu_canvas.create_image(CANVAS_WIDTH//2, 420, anchor='n', image=self.btn_quit_img, tags="quit_btn")

        self.menu_canvas.tag_bind("start_btn", "<Button-1>", lambda e: self.start_game())
        self.menu_canvas.tag_bind("ins_btn", "<Button-1>", lambda e: self.show_instructions())
        self.menu_canvas.tag_bind("quit_btn", "<Button-1>", lambda e: self.root.destroy())

    def show_instructions(self):
        # instructions popup
        self.snd_button_click.play()
        instructions = (
            "Welcome to Marksmania!!\n\n"
            "- Click targets on the screen to score points.\n"
            "- Different targets award different points:\n"
            "  * Red: 100 points\n"
            "  * Blue: 300 points\n"
            "  * Golden: 500 points\n"
            "- Blue targets will fall when they spawn.\n"
            "- Golden targets will teleport when hovered and have\n"
            "  a chance to spawn red targets when destroyed.\n"
            "- The game lasts 30 seconds.\n"
            "- Try to score as many points as possible!\n"
            "\nGood luck!"
            "\n Game by: @boxqd (github.com/boxqd)"
        )
        popup = tk.Toplevel(self.root)
        popup.title("Instructions")
        popup.geometry("400x400")
        popup.resizable(False, False)
        label = tk.Label(popup, text=instructions, font=("Arial", 12), justify="left", wraplength=380)
        label.pack(padx=20, pady=20)
        def on_ok():
            self.snd_button_click.play()
            popup.destroy()
        ok_button = tk.Button(popup, text="OK", command=on_ok)
        ok_button.pack(pady=10)

    def start_game(self):
        # starts the actual game
        self.snd_game_start.play()
        time.sleep(1.5)
        pygame.mixer.music.load('sounds/bgm.mp3')
        pygame.mixer.music.set_volume(VOLUME_BGM)
        pygame.mixer.music.play(-1)
        self.menu_frame.pack_forget()
        self.game_frame.pack()
        self.POINTS = 0
        self.ACTIVE_TARGETS.clear()
        self.IMAGE_REFERENCES.clear()
        self.GAME_ACTIVE = True
        self.time_left = GAME_DURATION
        self.create_bg(self.canvas)
        self.score_label.config(text=f"Score: {self.POINTS}")
        self.score_label.place(x=CANVAS_WIDTH - 10, y=CANVAS_HEIGHT - 10, anchor='se')
        self.timer_label.config(text=self.format_time(self.time_left))
        self.timer_label.place(x=10, y=CANVAS_HEIGHT - 10, anchor='sw')
        self.endgame_frame.place_forget()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.start_game_timer(self.canvas, self.end_game)
        self.game_loop()

    def retry_game(self):
        # just restarts
        self.canvas.delete("all")
        self.start_game()

    def play_spot_x(self):
        # random x within the bounds
        return random.randint(0, CANVAS_WIDTH - 50)

    def play_spot_y(self):
        # random y within the bounds
        return random.randint(0, GROUND_SURFACE - 50)

    def create_bg(self, canvas):
        # bg image
        canvas.delete("all")
        bg_img = Image.open('images/background.png').resize(((CANVAS_WIDTH + 10), (CANVAS_HEIGHT + 10)), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)
        canvas.create_image(0, 0, anchor='nw', image=self.bg_image)

    def create_target_img(self, canvas, x, y, img_name):
        # makes a target image
        pil_image = Image.open(img_name)
        pil_image = pil_image.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        target_image_id = canvas.create_image(x, y, image=tk_image, anchor='nw')
        self.IMAGE_REFERENCES[target_image_id] = tk_image
        return target_image_id

    def change_target_img(self, canvas, target_id, new_image_name):
        # change image
        pil_image = Image.open(new_image_name)
        pil_image = pil_image.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        self.IMAGE_REFERENCES[target_id] = tk_image
        canvas.itemconfig(target_id, image=tk_image)

    def remove_target(self, canvas, target_id):
        # remove from canvas and dicts
        canvas.delete(target_id)
        if target_id in self.IMAGE_REFERENCES:
            del self.IMAGE_REFERENCES[target_id]
        if target_id in self.ACTIVE_TARGETS:
            del self.ACTIVE_TARGETS[target_id]

    def start_game_timer(self, canvas, end_game_callback):
        # timer stuff
        def update_timer():
            if self.time_left > 0 and self.GAME_ACTIVE:
                self.time_left -= 1000
                self.timer_label.config(text=self.format_time(self.time_left))
                self.game_timer_id = canvas.after(1000, update_timer)
            else:
                self.GAME_ACTIVE = False
                end_game_callback()
        update_timer()

    def cleanup_and_quit(self):
        # quit everything, kept getting some errors when quitting, this and final_quit should fix it
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            self.root.after(100, self.final_quit)
        except Exception:
            self.root.destroy()

    def final_quit(self):
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()

    def end_game(self):
        # game over stuff
        self.GAME_ACTIVE = False
        pygame.mixer.music.stop()
        if self.game_timer_id:
            self.canvas.after_cancel(self.game_timer_id)
            self.game_timer_id = None
        print("Game Over!")
        self.canvas.delete("all")
        self.score_label.place_forget()
        self.timer_label.place_forget()
        menubg_img = Image.open('images/menubg.png').resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)
        self.menu_bg_photo = ImageTk.PhotoImage(menubg_img)
        self.canvas.create_image(0, 0, anchor='nw', image=self.menu_bg_photo)
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 50, text=f"Final Score: {self.POINTS}", font=("Arial", 24), fill="black")
        self.btn_retry_img = ImageTk.PhotoImage(Image.open('images/btn_retry.png').resize((220, 60), Image.LANCZOS))
        self.btn_quit_img = ImageTk.PhotoImage(Image.open('images/btn_quit.png').resize((220, 60), Image.LANCZOS))
        retry_btn = self.canvas.create_image(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 20, anchor='n', image=self.btn_retry_img, tags="retry_btn")
        quit_btn = self.canvas.create_image(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 100, anchor='n', image=self.btn_quit_img, tags="quit_btn")
        self.canvas.tag_bind("retry_btn", "<Button-1>", lambda e: self.retry_game())
        self.canvas.tag_bind("quit_btn", "<Button-1>", lambda e: self.cleanup_and_quit())

    def spawn_standard_targets(self, canvas, x, y):
        # makes 1-3 normal targets
        if not self.GAME_ACTIVE:
            return
        for _ in range(random.randint(1, 3)):
            tx, ty = self.play_spot_x(), self.play_spot_y()
            target_id = self.create_target_img(canvas, tx, ty, 'images/mmnTarget1.png')
            self.ACTIVE_TARGETS[target_id] = {'x': tx, 'y': ty, 'type': 'standard'}

    def create_medium_target(self, canvas):
        # blue target
        if not self.GAME_ACTIVE:
            return
        tx, ty = self.play_spot_x(), self.play_spot_y()
        target_id = self.create_target_img(canvas, tx, ty, 'images/mmnTarget2.png')
        self.ACTIVE_TARGETS[target_id] = {'x': tx, 'y': ty, 'type': 'medium'}
        self.move_medium_target(canvas, target_id, ty)

    def move_medium_target(self, canvas, target_id, current_y):
        # blue target falls
        if target_id not in self.ACTIVE_TARGETS or not self.GAME_ACTIVE:
            return
        if current_y < (GROUND_SURFACE - TARGET_SIZE):
            canvas.move(target_id, 0, 10)
            self.ACTIVE_TARGETS[target_id]['y'] = current_y + 10
            canvas.after(50, lambda: self.move_medium_target(canvas, target_id, current_y + 10))
        else:
            canvas.after(50, lambda: self.remove_target(canvas, target_id))

    def create_hard_target(self, canvas):
        # golden WIND!!!! target (yes that was a jojo reference)
        if not self.GAME_ACTIVE:
            return
        tx, ty = self.play_spot_x(), self.play_spot_y()
        target_id = self.create_target_img(canvas, tx, ty, 'images/mmnTarget3.png')
        self.ACTIVE_TARGETS[target_id] = {
            'x': tx,
            'y': ty,
            'type': 'hard',
            'teleports_left': 2,
            'timer_id': None
        }
        def remove_with_check(tid=target_id):
            # remove target if it still exists
            if tid in self.ACTIVE_TARGETS:
                self.remove_target(canvas, tid)
        def start_hard_timer(tid=target_id):
            if tid in self.ACTIVE_TARGETS and self.ACTIVE_TARGETS[tid].get('timer_id'):
                canvas.after_cancel(self.ACTIVE_TARGETS[tid]['timer_id'])
            timer_id = canvas.after(TARGET_LIFETIME, lambda: remove_with_check(tid))
            if tid in self.ACTIVE_TARGETS:
                self.ACTIVE_TARGETS[tid]['timer_id'] = timer_id
        def on_hover(event, tid=target_id):
            if tid in self.ACTIVE_TARGETS and self.ACTIVE_TARGETS[tid]['teleports_left'] > 0 and self.GAME_ACTIVE:
                self.teleport_hard_target(canvas, tid, start_hard_timer)
                self.ACTIVE_TARGETS[tid]['teleports_left'] -= 1
        canvas.tag_bind(target_id, "<Enter>", on_hover)
        start_hard_timer(target_id)

    def teleport_hard_target(self, canvas, target_id, timer_callback=None):
        # gold target teleports, now you see me, now you don't
        if target_id not in self.ACTIVE_TARGETS or not self.GAME_ACTIVE:
            return
        new_x, new_y = self.play_spot_x(), self.play_spot_y()
        old_x, old_y = self.ACTIVE_TARGETS[target_id]['x'], self.ACTIVE_TARGETS[target_id]['y']
        canvas.move(target_id, new_x - old_x, new_y - old_y)
        self.ACTIVE_TARGETS[target_id]['x'] = new_x
        self.ACTIVE_TARGETS[target_id]['y'] = new_y
        if timer_callback:
            timer_callback(target_id)

    def on_canvas_click(self, event):
        # click on targets, handle what happens such as scoring and removing targets
        if not self.GAME_ACTIVE:
            return
        x_click, y_click = event.x, event.y
        clicked_items = self.canvas.find_overlapping(x_click, y_click, x_click, y_click)
        for item in clicked_items:
            if item in self.ACTIVE_TARGETS:
                if self.ACTIVE_TARGETS[item].get('clicked', False):
                    continue
                self.ACTIVE_TARGETS[item]['clicked'] = True
                self.snd_target_hit.play()
                target_data = self.ACTIVE_TARGETS[item]
                target_type = target_data['type']
                if target_type == 'medium':
                    self.change_target_img(self.canvas, item, 'images/mmndestroy2.png')
                    self.POINTS += 300
                    self.canvas.after(500, lambda tid=item: self.remove_target(self.canvas, tid))
                elif target_type == 'hard':
                    self.change_target_img(self.canvas, item, 'images/mmndestroy3.png')
                    chance = random.randint(1, 100)
                    if chance >= 70:
                        self.spawn_standard_targets(self.canvas, target_data['x'], target_data['y'])
                    self.POINTS += 500
                    self.canvas.after(500, lambda tid=item: self.remove_target(self.canvas, tid))
                else:
                    self.change_target_img(self.canvas, item, 'images/mmndestroy1.png')
                    self.POINTS += 100
                    self.canvas.after(500, lambda tid=item: self.remove_target(self.canvas, tid))
                self.score_label.config(text=f"Score: {self.POINTS}")
                print(f"Score: {self.POINTS}")
                break

    def spawn_target(self):
        # makes targets
        if not self.GAME_ACTIVE:
            return
        if len(self.ACTIVE_TARGETS) < 10:
            target_type = random.choices(
                ['standard', 'medium', 'hard'], weights=[50, 30, 20], k=1)[0]
            if target_type == 'standard':
                tx, ty = self.play_spot_x(), self.play_spot_y()
                target_id = self.create_target_img(self.canvas, tx, ty, 'images/mmnTarget1.png')
                self.ACTIVE_TARGETS[target_id] = {'x': tx, 'y': ty, 'type': 'standard'}
                self.canvas.after(TARGET_LIFETIME, lambda tid=target_id: self.remove_target(self.canvas, tid) if tid in self.ACTIVE_TARGETS else None)
            elif target_type == 'medium':
                self.create_medium_target(self.canvas)
            elif target_type == 'hard':
                self.create_hard_target(self.canvas)

    def game_loop(self):
        # main loop
        if self.GAME_ACTIVE:
            chance = random.randint(1, 100)
            if chance >= 80:
                for _ in range(2):
                    self.spawn_target()
            elif chance >= 95:
                for _ in range(3):
                    self.spawn_target()
            else:
                self.spawn_target()
            self.root.after(1000, self.game_loop)

def main():
    # run game
    root = tk.Tk()
    game = MarksMania(root)
    root.mainloop()

if __name__ == '__main__':
    # no touchy touchy, otherwise it hurty hurty
    main()
