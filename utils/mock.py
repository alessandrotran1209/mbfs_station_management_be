import re
import sys

patterns = {
    '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
    '[đ]': 'd',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y'
}


def convert(text):
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """
    output = text
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        # deal with upper case
        output = re.sub(regex.upper(), replace.upper(), output)
    return output


names = ['Bùi Văn Dũng', 'Trần Ngọc Trung', 'Lê Trọng Hào', 'Đỗ Văn Đoan', 'Trần Quang Trung', 'Nguyễn Văn Duy',
         'Phạm Huy Bình', 'Nguyễn Đức Khôi', 'Vũ Đức Tụ', 'Trương Thanh Đồng', 'Phạm Như Việt', 'Phạm Thế Anh',
         'Vũ Quang Sinh', 'Phạm Cao Khải', 'Nguyễn Hữu Tài', 'Nguyễn Ngọc Sáng', 'Đồng Văn Toản', 'Trần Tiến Hà',
         'Đào Xuân Dũng', 'Nguyễn Anh Hùng', 'Lê Ngọc Anh', 'Vũ Tuấn Anh', 'Nguyễn Mạnh Tường', 'Nguyễn Văn Thọ',
         'Lê Hồng Nhật', 'Hoàng Văn Quý', 'Lê Trọng Văn', 'Nguyễn Tiến Điệp', 'Đỗ Xuân Viện', 'Lê Trọng Linh',
         'Nguyễn Khắc Tuân', 'Trần Hoàng Hải', 'Phan Tiến Dũng', 'Tiết Văn Việt', 'Nguyễn Công Nguyên', 'Võ Văn Quyền',
         'Phí Văn Hiếu', 'Trần Văn Táo', 'Phạm Thành Chung', 'Đặng Thế Đạt', 'Nguyễn Văn Tưởng', 'Lê Đình Giảng',
         'Bùi Duy Đoàn', 'Phạm Hồng Hải', 'Phạm Xuân Tình', 'Trần Anh Dũng', 'Trần Văn Nam', 'Lê Ngọc Thiên',
         'Trương Văn Nhu', 'Nguyễn Văn Ngọc', 'Trần Hoàng Hạnh', 'Nguyễn Đình Tuấn', 'Hoàng Văn Thành',
         'Trần Thành Chung', 'Trương Đình Kiên', 'Nguyễn Mạnh Hùng', 'Trịnh Văn Tiến', 'Nguyễn Đại Nam',
         'Lê Trung Hiếu', 'Lê Xuân Thảo', 'Lưu Trọng Vũ', 'Trịnh Văn Chung', 'Ngô Xuân Lâm', 'Nguyễn Mậu Huy',
         'Trần Văn Phương', 'Lê Văn Kiên', 'Trần Thế Thanh', 'Nguyễn Văn Công', 'Trương Xuân Thành', 'Trịnh Công Sơn',
         'Lê Đình Tuấn', 'Phan Đình Hải', 'Trương Đắc Tuấn', 'Đinh Đức Hưởng', 'Hoàng Văn Hòa', 'Lê Văn Cường',
         'Vũ Văn Hùng', 'Tôn Viết Thành', 'Nguyễn Ngọc Hoàng Anh', 'Nguyễn Ngọc Kiên', 'Đỗ Văn Duy', 'Tôn Viết Thắng',
         'Hoàng Văn Bắc', 'Nguyễn Bật Tân', 'Đinh Đức Hướng', 'Lê Hùng Mạnh', 'Nguyễn Phi Hùng', 'Lê Văn Dũng',
         'Phạm Văn Lộc', 'Trần Hữu Tài', 'Nguyễn Mạnh Ninh', 'Hoàng Đức Cường', 'Hồ Quang Tiến', 'Trịnh Viết Thình',
         'Lê Bật Sơn', 'Nguyễn Ngọc Tiến', 'Nguyễn Văn Hóa', 'Nguyễn Cảnh Hiếu', 'Đăng Văn Quang', 'Nguyễn Tuấn Anh',
         'Nguyễn Văn Trường', 'Phạm Đình Trưởng', 'Nguyễn Hoàng Hiệp', 'Nguyễn Cảnh Linh', 'Hồ Quang Mạnh',
         'Nguyễn Văn Tâm', 'Vũ Ngọc Hiến', 'Phan Quang Sáng', 'Lại Văn Nam', 'Đinh Văn Thương', 'Trần Văn Điển',
         'Nguyễn Anh Tuấn', 'Đàm Văn Toàn', 'Phạm Đức Hà', 'Hoàng Văn Hà', 'Ngô Quốc Bảo', 'Vũ Văn Đông',
         'Lê Văn Công Trường', 'Nguyễn Thanh Hiệp', 'Trần Văn Dũng', 'Cao Mạnh Thắng', 'Phạm Hoàng Hải',
         'Phạm Văn Xuân', 'Trần Hoàng Hải', 'Tạ Quang Thịnh', 'Nguyễn Đình Tuấn', 'Lê Công Thư', 'Trịnh Tuấn Hải',
         'Phạm Văn Linh', 'Lê Tân Tùng', 'Phạm Văn Khoa', 'Nguyễn Bá Hải', 'Nguyễn Đình Văn', 'Trần Ngọc Anh',
         'Lâm Ngọc Thức', 'Nguyễn Thanh Tùng', 'Phạm Ngọc Hiếu', 'Phạm Hồng Huy', 'Nguyễn Quốc Cường',
         'Đinh Xuân Phương', 'Phạm Hữu Khải', 'Trịnh Bùi Thoại', 'Nguyễn Thế Trường', 'Nguyễn Ngọc Hải',
         'Trần Hoàng Hạnh', 'Trương Đình Ninh', 'Vi Văn Thống', 'Nguyễn Văn Thật', 'Đàm Quang Vượng', 'Cầm Bá Tùng',
         'Phạm Xuân Lộc', 'Nguyễn Viết Đoàn', 'Trịnh Công Sơn', 'Nguyễn Văn Hùng', 'Lê Khắc Thế', 'Vũ Văn Huyên',
         'Lương Viết Tiến', 'Đặng Văn Hiệu', 'Vũ Mạnh Thảo', 'Lê Cảnh Tài', 'Nguyễn Đình Trường',
         'Bùi Thành Chung']

usernames = []
for name in names:
    try:
        name_break_down = name.split()
        username = convert(name_break_down[-1])
        for i in range(0, len(name_break_down) - 1):
            username += convert(name_break_down[i][0])
        usernames.append(username.lower())
    except:
        raise Exception(name)
results = ['thatnv', 'haolt', 'phuongdx', 'hainb', 'diepnt', 'thinhtq', 'thangtv', 'thonv', 'datdt', 'baonq', 'tuantd',
           'tungnt', 'dungdx', 'truongnt', 'huongdd', 'nguyennc', 'thanhtt', 'vietpn', 'tienlv', 'manhlh', 'doandv',
           'tuongnm', 'truongnd', 'dunglv', 'linhnc', 'hoanv', 'khaipc', 'tinhpx', 'quyhv', 'trungtq', 'haith',
           'anhnnh', 'khoapv', 'nhatlh', 'hienvn', 'truongnv', 'huynm', 'toandv', 'hieunc', 'hiepnt', 'duydv', 'tientv',
           'doanbd', 'tuvd', 'lamnx', 'hieupv', 'ninhnm', 'thienln', 'thanhtx', 'namlv', 'kientd', 'cuonglv', 'binhph',
           'anhln', 'dongtt', 'phuongtv', 'kienlv', 'thaovm', 'haiph', 'namtv', 'hảith', 'linhpv', 'hainn', 'thulc',
           'huyph', 'haiph', 'vuongdq', 'hungnp', 'tunglt', 'thuongdv', 'giangld', 'tuanld', 'anhvt', 'hahv', 'thoaitb',
           'chungbt', 'hoahv', 'chungtv', 'tamnv', 'anhtn', 'huongdd', 'khaiph', 'congnv', 'tiennn', 'tuannd',
           'tuongnv', 'cuongnq', 'sangpq', 'hieupn', 'quangdv', 'bachv', 'tailc', 'sontc', 'anhpt', 'hatt', 'duynv',
           'khoind', 'dungbv', 'linhlt', 'hanhth', 'thanhhv', 'tienhq', 'vannd', 'locpx', 'taotv', 'huyenvv', 'vult',
           'xuanpv', 'kiennn', 'ngocnv', 'tannb', 'dungta', 'viettv', 'tuannk', 'anhnt', 'truongpd', 'hungna',
           'tuánnd', 'thaolx', 'sangnn', 'taith', 'cuonghd', 'thinhtv', 'namnd', 'vanlt', 'ninhtd', 'tungcb', 'manhhq',
           'doannv', 'dungpt', 'viendx', 'locpv', 'dongvv', 'hieudv', 'thelk', 'truonglvc', 'chungpt', 'toandv',
           'hungvv', 'hạnhth', 'thangcm', 'hieult', 'sontc', 'dungtv', 'sonlb', 'tuanna', 'haitt', 'hapd', 'dientv',
           'thucln', 'thanhtv', 'hiepnh', 'chungtt', 'sinhvq', 'quyenvv', 'hungnm', 'haipd', 'tainh', 'thongvv',
           'trungtn', 'nhutv', 'hungnv']

