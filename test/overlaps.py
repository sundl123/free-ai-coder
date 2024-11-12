def find_overlap(str1: str, str2: str) -> tuple[bool, str]:
    """
    判断两个字符串是否存在重合部分（str1的尾部和str2的头部）

    Args:
        str1: 第一个字符串
        str2: 第二个字符串

    Returns:
        tuple[bool, str]: (是否重合, 重合部分的字符串)
    """
    # 获取较短字符串的长度
    min_len = min(len(str1), len(str2))

    # 从最长可能的重合开始检查
    for i in range(min_len, 0, -1):
        if str1[-i:] == str2[:i]:
            return True, str1[-i:]

    return False, ""


# 测试代码
def test_overlap():
    test_cases = [
        ("hello", "lower"),  # "lo" 重合
        ("abc", "cde"),  # "c" 重合
        ("python", "online"),  # "on" 重合
        ("cat", "dog"),  # 无重合
        ("test", "testing"),  # "test" 重合
        ("a", "a"),  # "a" 重合
        ("", "test"),  # 无重合
        ("xyz", "abc"),  # 无重合
    ]

    for str1, str2 in test_cases:
        has_overlap, overlap = find_overlap(str1, str2)
        if has_overlap:
            print(f"'{str1}' 和 '{str2}' 重合，重合部分是 '{overlap}'")
        else:
            print(f"'{str1}' 和 '{str2}' 没有重合")


# 运行测试
if __name__ == "__main__":
    test_overlap()