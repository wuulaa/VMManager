def format_strings(arr):
    formatted_arr = []
    for s in arr:
        if s is not None:
            # 如果字符串不为空，去除密码并添加到格式化数组中
            parts = s.split(":")
            if len(parts) == 3:
                ip_port = f"{parts[0]}:{parts[1]}"
                formatted_arr.append(ip_port)
            else:
                formatted_arr.append(s)
        else:
            # 如果字符串为None，添加None到格式化数组中
            formatted_arr.append(None)
    return formatted_arr

def is_string_in_array(s, arr):
    formatted_arr = format_strings(arr)
    return s in formatted_arr

# 示例用法
string_to_check = "192.168.0.1:8080"
string_array = ["192.168.0.1:8080:password", None, "invalid_string"]

formatted_array = format_strings(string_array)
result = is_string_in_array(string_to_check, string_array)

print("Formatted Array:", formatted_array)
print(f"Is '{string_to_check}' in the array? {result}")
