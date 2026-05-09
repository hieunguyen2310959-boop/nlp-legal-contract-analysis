
text = "trường hợp đánh giá, xếp loại chất lượng viên chức theo năm học thì thời điểm tiến hành đánh giá, xếp loại chất lượng viên chức trước ngày 15 tháng 9 hằng năm."
entity = "ngày 15 tháng 9"
start = text.find(entity)
end = start + len(entity)
print(f"Start: {start}, End: {end}")
