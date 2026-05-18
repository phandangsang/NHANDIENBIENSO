# Database cho ung dung nhan dien bien so bai do xe

Database dung MySQL, tap trung vao viec luu xe vao/ra va anh nhan dien.

## Cac bang

| Bang | Muc dich |
| --- | --- |
| `user` | Luu tai khoan nguoi dung he thong (bang nay duoc quote bang backticks khi query) |
| `vehicle` | Luu bien so va loai xe |
| `parking_records` | Luu tung luot xe vao/ra bai |
| `images` | Luu duong dan anh xe, anh bien so va ket qua nhan dien |

## Luong xe vao

1. Nhan dien bien so xe.
2. Tim hoac tao xe trong bang `vehicle`.
3. Tao ban ghi trong `parking_records` voi `status = 'in'`.
4. Luu anh vao bang `images` voi `image_type = 'entry'`.

## Luong xe ra

1. Nhan dien bien so xe.
2. Tim xe trong bang `vehicle`.
3. Tim ban ghi dang gui trong `parking_records` voi `status = 'in'`.
4. Cap nhat `exit_time` va `status = 'out'`.
5. Luu anh vao bang `images` voi `image_type = 'exit'`.
