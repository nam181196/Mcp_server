# Sử dụng image Python chuẩn và gọn nhẹ
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements.txt vào trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Thiết lập biến môi trường mặc định để chạy qua SSE
ENV MCP_TRANSPORT=sse
ENV MCP_PORT=8000
ENV MCP_HOST=0.0.0.0

# Expose port 8000 ra ngoài
EXPOSE 8000

# Lệnh khởi chạy server
CMD ["python", "server.py"]
