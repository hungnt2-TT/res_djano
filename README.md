# Quản Lý Chuỗi Cửa Hàng - Dự Án Django

Dự án này sử dụng Django để xây dựng một hệ thống quản lý chuỗi cửa hàng. Nó bao gồm các chức năng như quản lý sản phẩm,
quản lý nhân viên, quản lý kho hàng, và nhiều hơn nữa.

## Các chức năng

- Đăng nhập và đăng ký
- Quản lý sản phẩm
- Quản lý nhân viên
- Quản lý kho hàng
- Quản lý đơn hàng
- Thống kê doanh số
- Và nhiều chức năng khác

## Yêu cầu

- Docker
- Docker Compose

## Cài đặt

Đảm bảo bạn đã cài đặt Docker và Docker Compose trên máy của bạn. Sau đó, bạn có thể sử dụng Docker Compose để cài đặt
và chạy dự án.

1. Clone dự án từ GitHub:

```bash
git clone https://github.com/yourusername/res_djano.git
```

2. Di chuyển vào thư mục dự án:

```bash
cd res_django
```

3. Tạo file `.env` từ file mẫu `.env.example`:

```bash
cp .env.example .env
```

4. Chạy dự án với Docker Compose:

```bash
docker-compose up
```

5. Mở trình duyệt và truy cập vào `http://localhost:8000` để xem dự án.
6. Đăng nhập với tài khoản mặc định:
7. Tên đăng nhập: `admin`
8. Mật khẩu: `admin`
9. Để dừng dự án, bạn có thể sử dụng tổ hợp phím `Ctrl + C` trong cửa sổ terminal.
10. Để xóa dự án, bạn có thể sử dụng lệnh sau:

```bash
docker-compose down
```

