groups = {
    'hni-1': "1",
    'hni-2': "2",
    'hni-3': "3",
    'haiduong': "Hải Dương",
    'hungyen': "Hưng Yên",
    'thaibinh': "Thái Bình",
    'thanhhoa': "Thanh Hóa",
    'nghean': "Nghệ An",
    'quangbinh': "Quảng Bình",
    'hatinh': "Hà Tĩnh",
}

def get_group_username():
    return [key for key, _ in groups.items()]

def get_group_value(key):
    return groups[key] if key in groups else ''