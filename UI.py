
import tkinter as tk
from tkinter import ttk  # Thư viện hỗ trợ cho combobox

# if __name__ == "AIProjectData":
# Hàm xử lý khi nhấn nút chạy
def process_inputs():
    global fuel_capacity, NumberOfLevelsandStations, NumberLevel
    # Lấy giá trị từ dropdown menu và textbox
    selected_option = option_var.get()
    numbers_input = textbox.get("1.0", tk.END).strip()
    
    # Chuyển đổi chuỗi số nguyên thành danh sách
    numbers_list = list(map(int, numbers_input.split()))
    
    # Tiến hành xử lý hoặc hiển thị các giá trị (ví dụ in ra console hoặc gửi vào output area)
    print(f"Selected Option: {selected_option}")
    print("Entered Numbers: ", numbers_list)
    fuel_capacity = int(selected_option)
    NumberOfLevelsandStations = numbers_list[0]
    NumberLevel = numbers_list[1:]

    root.destroy()

    # Giả sử xử lý và lưu vào file output.txt ở đây...
    # ... (lưu ý cập nhật logic xử lý tùy thuộc vào yêu cầu cụ thể)
    
    # Hiển thị output từ file
#     show_output()

# # Hàm hiển thị nội dung file output
# # def show_output():
# #     # Đường dẫn tới file output của bạn, giả sử là "output.txt"
# #     file_path = "output.txt"
    
# #     # Đọc nội dung file
# #     with open(file_path, "r") as file:
# #         content = file.read()
    
    # Xóa nội dung cũ và hiển thị nội dung mới
    # output_area.delete("1.0", tk.END)
    # output_area.insert(tk.END, content)

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Nhập và Xử lý Dữ Liệu")

# Tạo và đặt dropdown menu
option_var = tk.StringVar()  # Biến lưu giá trị chọn
options = ['100', '150', '200', '250', '300']
option_menu = ttk.Combobox(root, textvariable=option_var, values=options)
option_menu.pack()

# Tạo textbox để nhập nhiều số nguyên
textbox = tk.Text(root, height=10, width=30)
textbox.pack()

# # Tạo output area để hiển thị nội dung file
# output_area = tk.Text(root, height=20, width=60)
# output_area.pack()


# Tạo nút chạy và gắn hàm process_inputs
run_button = tk.Button(root, text="Xử lý", command=process_inputs)
# run_button.bind("<Button-1>", close_window)
run_button.pack()

# Chạy vòng lặp chính của ứng dụng

root.wait_window()
