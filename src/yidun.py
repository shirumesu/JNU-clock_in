import cv2
import random
import numpy as np
from PIL import Image
from typing import Optional, Callable, List


class yidun:
    def crack(self, target_img: str, template_img: str, xp: int = 320) -> List[int]:
        """易盾破解一条龙(?)

        Args:
            target_img (str): 带缺口的待拼合图片路径(本地)
            template_img (str): 拼图图片路径(本地)
            xp (int, optional): 验证码的大小,易盾默认为320,应该不需要改变. Defaults to 320.

        Returns:
            List[int]: 每次应该移动的幅度 直到拼图完全合并(模拟人类行为 由快至慢 中间会超过合并位置并慢慢退回来)
        """
        zoom = xp / int(Image.open(target_img).size[0])

        distance = self.match(target_img, template_img)

        return self.get_tracks((distance + 7) * zoom)

    def change_size(self, file):
        image = cv2.imread(file, 1)
        img = cv2.medianBlur(image, 5)
        b = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)
        binary_image = b[1]
        binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
        x, y = binary_image.shape
        edges_x = []
        edges_y = []
        for i in range(x):
            for j in range(y):
                if binary_image[i][j] == 255:
                    edges_x.append(i)
                    edges_y.append(j)

        left = min(edges_x)
        right = max(edges_x)
        width = right - left
        bottom = min(edges_y)
        top = max(edges_y)
        height = top - bottom
        pre1_picture = image[left : left + width, bottom : bottom + height]
        return pre1_picture

    def match(self, target, temp) -> int:
        img_gray = cv2.imread(target, 0)
        img_rgb = self.change_size(temp)
        template = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        run = 1

        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            if threshold < 0:
                print("Error")
                return None
            loc = np.where(res >= threshold)
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]

    def get_tracks(
        self,
        distance: int,
        seconds: int = random.randint(2, 4),
        ease_func: Optional[Callable] = lambda x: 1 - pow(1 - x, 4),
    ):
        distance += 20
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            offset = round(ease_func(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])

        while 0 in tracks:
            tracks.remove(0)

        return tracks
