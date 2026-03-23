def map_error_feedback(stderr: str, exit_code: int) -> str:
    text = stderr or ""
    if "NameError" in text:
        return "Bạn đang dùng biến chưa được tạo. Hãy khai báo biến trước nhé."
    if "SyntaxError" in text:
        return "Có lỗi cú pháp. Kiểm tra dấu ngoặc, dấu : và thụt dòng."
    if "IndentationError" in text:
        return "Thụt dòng chưa đúng. Hãy căn lề lại cho đúng nhé."
    if "TypeError" in text:
        return "Có lỗi về kiểu dữ liệu. Hãy kiểm tra cách bạn dùng biến."
    if exit_code != 0:
        return "Có lỗi khi chạy. Hãy thử lại và xem lại mã của bạn."
    return "Có lỗi khi chạy. Hãy thử lại."


def map_mismatch_feedback(_challenge: dict) -> str:
    return "Kết quả chưa đúng. Hãy xem lại gợi ý và thử lại nhé."


def map_success_feedback(challenge: dict) -> str:
    return challenge.get("success", "Tốt lắm! Bạn đã hoàn thành bài này.")
