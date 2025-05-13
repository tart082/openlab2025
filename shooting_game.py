# -*- coding: utf-8 -*-
import sys
import pygame
from pygame.locals import *

import cv2
import mediapipe as mp
import numpy as np
import random
import math

# Mediapipeの初期化
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # 片手のみトラッキング
mp_drawing = mp.solutions.drawing_utils

# Webカメラの入力を取得
camera_index = 0
# camera_index = 1 # 環境依存適宜変更
print("camera_index =", camera_index)
cap = cv2.VideoCapture(camera_index)

# 人差し指の軌跡を保存するためのリスト
trajectory = []

# 画面サイズ
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
hight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
SCREEN_SIZE = (width, hight)
print(SCREEN_SIZE)


# 画像の読み込み
ufo_image = pygame.image.load("images/alien_ufo.png") # (400*315)
ufo_image = pygame.transform.scale(ufo_image, (50, 40)) # 画像を指定サイズに縮小
rocket_image = pygame.image.load("images/space_saturnV_rocket_apollo11.png") # (261*500)
rocket_image = pygame.transform.scale(rocket_image, (26, 50)) # 画像を縮小
alien_bullet_image = pygame.image.load("images/sports_balance_ball.png") # (400*400)
alien_bullet_image = pygame.transform.scale(alien_bullet_image, (10, 10))
silver_bullet_image = pygame.image.load("images/gin_dangan_silver_bullet.png") # (262*400)
silver_bullet_image = pygame.transform.scale(silver_bullet_image, (10, 20))
barrier_image = pygame.image.load("images/barrier_hemisphere.png") # (400*309)
barrier_image = pygame.transform.scale(barrier_image, (80, 62))
open_hand_image = pygame.image.load("images/virus_hand_clean.png") # (612*612)
open_hand_image = pygame.transform.scale(open_hand_image, (60, 60))
pointing_up_image = pygame.image.load("images/pose_hitosashiyubi.png") # (290*400)
pointing_up_image = pygame.transform.scale(pointing_up_image, (44, 60))
pinch_image = pygame.image.load("images/body_finger_ok.png") # (400, 400)
pinch_image = pygame.transform.scale(pinch_image, (60,60))

def detect_gesture(landmarks):
    """
    ジェスチャーを判定する関数。
    - 人差し指(ランドマーク8)と親指(ランドマーク4)の位置関係で簡易的な判定を行う
    """
    # 各ランドマークの座標を取得
    index_tip = landmarks.landmark[8]  # 人差し指先
    thumb_tip = landmarks.landmark[4]  # 親指先
    middle_tip = landmarks.landmark[12]  # 中指先

    # 距離計算用（スクリーン座標にスケーリング）
    index_thumb_dist = np.sqrt((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)
    index_middle_dist = np.sqrt((index_tip.x - middle_tip.x)**2 + (index_tip.y - middle_tip.y)**2)

    # 簡単なジェスチャー判定ロジック
    if index_thumb_dist < 0.05:  # 親指と人差し指が近い
        return "Pinch"
    # elif index_middle_dist < 0.05:  # 人差し指と中指が近い
        # return "Peace"
    elif index_tip.y < thumb_tip.y and index_tip.y < middle_tip.y:  # 人差し指が他より高い
        return "Pointing Up"
    else:
        return "Open Hand"

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 40, 0)

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = pygame.Surface((10, 10))
        # self.image.fill(GREEN)
        self.image = rocket_image
        self.rect = self.image.get_rect() # 見た目判定
        self.rect.center = (width / 2, hight * (3/4))
        self.radius = 5 # 半径
        self.speed = 5
        
        self.finger = (0, 0)
        self.remaining_shot_cool_time = 0
        self.shot_cool_time = 10

        self.barrier_stock_max = 1
        self.barrier_stock = self.barrier_stock_max
        self.barrier_remaining_cool_time = 0
        self.barrier_cool_time = 150

    def update(self):
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT] and self.rect.left > 0:
        #     self.rect.x -= self.speed
        # if keys[pygame.K_RIGHT] and self.rect.right < width:
        #     self.rect.x += self.speed
        self.rect.center = self.finger
        if self.remaining_shot_cool_time > 0:
            self.remaining_shot_cool_time -= 1
        if self.barrier_remaining_cool_time > 0:
            self.barrier_remaining_cool_time -= 1
        elif self.barrier_stock < self.barrier_stock_max:
            self.barrier_stock += 1
            self.barrier_remaining_cool_time = self.barrier_cool_time

# エイリアンクラス
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # self.image = pygame.Surface((30, 30))
        # self.image.fill(RED)
        self.image = ufo_image # 画像
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.speed_x = 2
        self.speed_y = 40

        self.stop_count = 0


    def update(self):
        if self.stop_count == 0:
            self.rect.x += self.speed_x
        else:
            self.stop_count -= 4
            # self.image.fill((255 * (1 - self.stop_count / 100),0,255*self.stop_count / 100)) # 氷の残り時間だけ青い
        if self.rect.right >= width or self.rect.left <= 0:
            self.speed_x *= -1
            self.rect.y += self.speed_y
            self.rect.x += self.speed_x # 急落下バグ解消
        if self.rect.bottom <= 40 or self.rect.top >= hight - 40:
            self.speed_y *= -1
            self.rect.y += self.speed_y # 画面外に消えないように
        # デバッグモード
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] :
            self.rect.y += self.speed_y
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed_y

# 弾クラス
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # self.image = pygame.Surface((5, 10))
        # self.image.fill(GREEN)
        self.image = silver_bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = - hight / 60

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
# エイリアンの弾クラス
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_mag = 1):
        super().__init__()
        # self.image = pygame.Surface((5, 10))
        # self.image.fill(RED)
        self.image = alien_bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = 5
        self.speed = hight / 120 * speed_mag
        self.theta = math.pi/2 # 発射角

    def update(self):
        # self.rect.y += self.speed
        self.rect.x += self.speed * math.cos(self.theta)
        self.rect.y += self.speed * math.sin(self.theta)
        if self.rect.top >= hight or self.rect.left < 0 or self.rect.right >= width or self.rect.bottom < 0:
            self.kill()
    
    def angle(self, P_x, P_y): # 発射角を計算
        X = P_x - self.rect.x
        Y = P_y - self.rect.y
        self.theta = math.atan2(Y, X)

# バリアクラス
class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = barrier_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.default_effect_time = 90
        self.effect_time = self.default_effect_time # 1sec(30fps)
        self.alpha = 255 * (self.effect_time / self.default_effect_time) # 透明度
        
    def update(self):
        self.effect_time -= 1
        if self.effect_time <= 0:
            self.kill() # 時間経過で削除
        # print(self.effect_time)
        self.alpha = 255 * (self.effect_time / self.default_effect_time)
        self.image.set_alpha(self.alpha) # 透明度変更
        


def main(t = 60, full_screen = False):
    # 初期化
    pygame.init()
    # 画面サイズ
    if full_screen:
        screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN) # フルスクリーン表示
    else:
        screen = pygame.display.set_mode(SCREEN_SIZE) # ウィンドウ表示
    pygame.display.set_caption("Space Invaders")
    # フォントの設定
    font = pygame.font.SysFont(None, 55)
    # スプライトグループの作成
    all_sprites = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Player()
    alien_bullets = pygame.sprite.Group() # 敵の弾丸
    barriers = pygame.sprite.Group() # バリア
    all_sprites.add(player)
    for i in range(10):
        for j in range(3):
            alien = Alien(50 + i * ((width - 100) / 10), 50 + j * ((hight - 50) / 6))
            all_sprites.add(alien)
            aliens.add(alien)
    # スコアの初期化
    score = 0
    # タイマーの設定
    fire_timer = 60
    select_timer_max = 60
    select_timer = t
    score_timer = 0
    # circle = pygame.surface
    # フラグ
    running = True
    game_over = False
    game_clear = False
    game_started = False
    
    # 現在のジェスチャーを保持する変数
    current_gesture = "No gesture detected" 

    # while running:
    while running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # BGR画像をRGBに変換（MediapipeはRGB画像を使用するため）
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 反転 (鏡像のようにするため)
        image = cv2.flip(image, 1)

        # 画像を処理して手のランドマークを取得
        results = hands.process(image)
        
        # 画像をBGRに戻す
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x = int(hand_landmarks.landmark[8].x * width)
                y = int(hand_landmarks.landmark[8].y * hight)
                if 0 <= x <width and 0 <= y < hight:
                    player.finger = (x, y)
                    # player.rect.center = (x, y)
                current_gesture = detect_gesture(hand_landmarks)
                    
        for event in pygame.event.get(): # キーボード操作 ゲーム終了のEscのみ
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not game_clear:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                if event.key == pygame.K_s:
                    game_started = True
                if event.key == pygame.K_r and (game_over or game_clear):
                    main()  # リスタート
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()  # ESCキーが押されたら終了
                if event.key == pygame.K_w:
                    screen = pygame.display.set_mode(SCREEN_SIZE) # カメラの解像度に合わせたサイズ
                    full_screen = False
                if event.key == pygame.K_f:
                    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN) # フルスクリーン表示
                    full_screen = True


        if current_gesture == "Pinch":
            if not game_started:
                if select_timer <= 0:
                    game_started = True # ゲーム開始
                else:
                    select_timer -= 1 # タイマーを減少
            if game_over or game_clear:
                if select_timer <= 0:
                    main(0, full_screen)  # リスタート
                else:
                    select_timer -= 1 # タイマーを減少
        elif select_timer < select_timer_max:
            select_timer += 1 # タイマー増加

        if current_gesture == "Pointing Up" and player.remaining_shot_cool_time == 0 and not game_over and not game_clear and game_started:
            bullet = Bullet(player.rect.centerx, player.rect.top) # 自機から弾が出る
            all_sprites.add(bullet)
            bullets.add(bullet)
            player.remaining_shot_cool_time = player.shot_cool_time
        elif current_gesture == "Open Hand" and not game_over and not game_clear and game_started:
            # フリーズ機能
            # for alien in aliens:
            #     alien.stop_count = 100 # エイリアンのスピードを下げる
            # fire_timer = 30 # 攻撃されなくなる

            # バリア機能
            if player.barrier_stock > 0 and len(barriers) == 0:
                player.barrier_stock -= 1
                barrier = Barrier(player.rect.centerx, player.rect.top) # バリアが自機の位置に出る
                barriers.add(barrier)
                all_sprites.add(barrier)

        if not game_over and not game_clear and game_started:
            if fire_timer <= 0:
                probability = min(0.001 * score,1)                      # 発射確率
                fire_timer = max(60 -  4 * math.log(score+2, 2), 5)     # 攻撃周期
                speed_mag = 1/2 + (1/2 * min((0.001 * score), 1))       # 弾速倍率
                for alien in aliens:
                    if random.random() <= probability:
                        alien_bullet = AlienBullet(alien.rect.centerx, alien.rect.bottom, speed_mag)  # 敵から弾が出る
                        alien_bullet.angle(player.rect.x, player.rect.y) # 角度を変える
                        all_sprites.add(alien_bullet)
                        alien_bullets.add(alien_bullet)
            else:
                fire_timer -= 1

        if not game_over and not game_clear and game_started:
            # 更新
            all_sprites.update()
            # 衝突判定
            pygame.sprite.groupcollide(barriers, alien_bullets, False, True) # バリアにあたった弾は消える
            hits = pygame.sprite.groupcollide(bullets, aliens, True, True)
            # if hits:
            for i in hits:
                score += 30
            # ゲームクリア判定
            if not aliens:
                game_clear = True
                select_timer = select_timer_max
            # ゲームオーバー判定（エイリアンがプレイヤーの位置まで到達した場合）
            # for alien in aliens:
            #     if alien.rect.bottom >= player.rect.top:
            #         game_over = True
            
            # player_hits = pygame.sprite.spritecollideany(player, alien_bullets)
            for alien_bullet in alien_bullets:
                player_hits = pygame.sprite.collide_circle(player, alien_bullet) # 円で判定
                if player_hits:
                    game_over = True
                    select_timer = select_timer_max
            # 生存ボーナス得点増加
            score_timer += 1
            if score_timer % 30 == 0:
                score += len(aliens) // 3
        # 描画
        screen.fill(DARK_GREEN)
        # OpenCVのBGRからPygame用にRGBに変換
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # numpy配列 → pygame.Surfaceに変換
        frame_surface = pygame.surfarray.make_surface(np.flip(frame, axis=-1))  # axis=1で左右反転（カメラに合わせる）
        
        # サーフェスをscreenにblit（描画）
        screen.blit(pygame.transform.rotate(frame_surface, -90), (0, 0))  # 必要なら回転も

        all_sprites.draw(screen)

        # 選択タイマー表示
        if select_timer < select_timer_max  and (not game_started or game_over or game_clear):
            # pygame.draw.circle(screen, RED, player.finger, select_timer / 2, 5)
            x, y = player.finger
            pygame.draw.arc(screen, RED, (x - 25, y - 25, 50, 50), math.pi / 2, 2 * math.pi * ((select_timer_max - select_timer) / (select_timer_max)) + math.pi / 2, 5)
            # unyo = pygame.rect((player.finger),(60,60))
            # pygame.draw.circle(screen, RED, unyo, 0, 2 * math.pi * ((select_timer - 100) / 100), 5)
        # if not game_started or game_over or game_clear:
        #     print(select_timer)
        
        # タイマー表示
        if game_started and not game_over and not game_clear:
            r = 48
            w = 4
            x, y = width - r, hight - r             # 中心座標
            screen.blit(open_hand_image, (x - 30, y - 30))  # open_hand
            # バリアタイマー
            for i in range(player.barrier_stock + 1):
                if i == 0:
                    pygame.draw.arc(screen, GREEN, (x - r, y - r, r * 2, r * 2), math.pi / 2, 2 * math.pi * ((player.barrier_cool_time - player.barrier_remaining_cool_time) / (player.barrier_cool_time)) + math.pi / 2, w)
                else:
                    pygame.draw.arc(screen, GREEN, (x - r, y - r, r * 2, r * 2), 0, 2 * math.pi, w)
                r -= 8

            # ショットタイマー
            r = 48
            x -= r * 2
            screen.blit(pointing_up_image, (x - 22, y - 30)) # pointing_up
            pygame.draw.arc(screen, GREEN, (x - r, y - r, r * 2, r * 2), math.pi / 2, 2 * math.pi * ((player.shot_cool_time - player.remaining_shot_cool_time ) / (player.shot_cool_time)) + math.pi / 2, w)

        
        # スコア表示
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # ジェスチャー表示
        # gesture_text = font.render(f"gesture: {current_gesture}", True, WHITE)
        # screen.blit(gesture_text, (10, 50))
        if(current_gesture == "Open Hand"):
            screen.blit(open_hand_image, (30, 40))
        elif(current_gesture == "Pointing Up"):
            screen.blit(pointing_up_image, (30, 40))
        elif(current_gesture == "Pinch"):
            screen.blit(pinch_image, (30, 40))

        # 操作説明
        # how_to_shot_text = font.render(f"Shot: Pointing Up", True, WHITE)
        # screen.blit(how_to_shot_text, (10, 90))
        # how_to_freeze_text = font.render(f"Freeze: Open Hand", True, WHITE)
        # screen.blit(how_to_freeze_text, (10, 130))
        
        # ゲーム開始前
        if not game_started:
            start_text = font.render("Pinch to Start", True, WHITE)
            screen.blit(start_text, (width / 3, hight / 2 - 30))
        # ゲームオーバー表示
        if game_over:
            game_over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (width / 3, hight / 2 - 30))
            restart_text = font.render("Pinch to Restart", True, WHITE)
            screen.blit(restart_text, (width / 3, hight / 2 + 30))
            # スプライトグループを空にする
            all_sprites.empty()
            aliens.empty()
            bullets.empty()

        # ゲームクリア表示
        if game_clear:
            game_clear_text = font.render("GAME CLEAR", True, WHITE)
            screen.blit(game_clear_text, (width / 3, hight / 2 - 30))
            restart_text = font.render("Pinch to Restart", True, WHITE)
            screen.blit(restart_text, (width / 3, hight / 2 + 30))
            # スプライトグループを空にする
            all_sprites.empty()
            aliens.empty()
            bullets.empty()

        # 画面更新
        pygame.display.flip()
        # フレームレート
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()